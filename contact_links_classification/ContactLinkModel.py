import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
import logging
import time
import os
import csv
from bs4 import BeautifulSoup

# for deployment Model
from contact_links_classification.LinkProcessing import LinkProcessing

# for test Model
# from LinkProcessing import LinkProcessing

class ContactLinkModel:
    
    def __init__(self, model_name='bert-base-cased', num_labels=2, max_length=40):
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.tokenizer = None
        self.model = None
        self.linkProcessing = LinkProcessing()
        
    def load_from_huggingface(self):
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels= self.num_labels
        )

    def load_from_local(self, tokenizer_path='bert-base-cased', model_path='./contact_links_classification/Models/model_3/model_contact_40_maxlen_30_epochs'):
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path)
    
    def preprocess(self, texts, truncation=True, padding=True):
        return self.tokenizer(
            texts, 
            padding=padding,
            truncation=truncation,
            max_length=self.max_length, 
            return_tensors="pt"
        )

    def get_original_tokens(self, input_ids):
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
        return tokens

    def compute_metrics(self, preds, labels):
        preds = preds.argmax(-1)
        accuracy = accuracy_score(labels, preds)
        recall = recall_score(labels, preds, average='binary')
        precision = precision_score(labels, preds, average='binary')
        f1 = f1_score(labels, preds, average='binary')
        return accuracy, precision, recall, f1

    def train(self, train_texts, train_labels, val_texts, val_labels, num_epochs, batch_size):
        
        os.makedirs("./Models/model_3", exist_ok=True)
        model_save_path = f"./Models/model_3/model_contact_{self.max_length}_maxlen_{num_epochs}_epochs"

        train_encodings = self.preprocess(train_texts)
        val_encodings = self.preprocess(val_texts)

        train_dataset = Dataset(train_encodings, train_labels)
        val_dataset = Dataset(val_encodings, val_labels)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        
        optimizer = AdamW(self.model.parameters(), lr=2e-5)
        total_steps = len(train_loader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)


        csv_filename = f"{model_save_path}_info.csv"
        header = ["training_details"]
        is_empty = True
        
        start_time = time.time()
        for epoch in range(num_epochs):
            self.model.train()
            total_loss = 0
            for batch in train_loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                total_loss += loss.item()
                loss.backward()
                optimizer.step()
                scheduler.step()

            avg_train_loss = total_loss / len(train_loader)

            # Validation
            self.model.eval()
            val_preds, val_labels = [], []
            val_total_loss = 0.0
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(device)
                    attention_mask = batch['attention_mask'].to(device)
                    labels = batch['labels'].to(device)
                    outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                    logits = outputs.logits
                    val_preds.extend(logits.detach().cpu().numpy())
                    val_labels.extend(labels.cpu().numpy())
                    loss = outputs.loss
                    val_total_loss += loss.item()

            avg_val_loss = val_total_loss / len(val_loader)

            val_preds = np.array(val_preds)
            val_labels = np.array(val_labels)
            accuracy, precision, recall, f1 = self.compute_metrics(val_preds, val_labels)

            training_details = (f"Époque {epoch+1}/{num_epochs} - Train Loss: {avg_train_loss:.4f} - "
                                f"Validation Loss: {avg_val_loss:.4f} - Validation Accuracy: {accuracy:.4f} - "
                                f"Precision: {precision:.4f} - Recall: {recall:.4f} - F1 Score: {f1:.4f}")
            print(training_details)
        
            with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                csv_writer = csv.writer(csvfile)
                if is_empty:
                    csv_writer.writerow(header)
                    is_empty = False
                csv_writer.writerow([training_details])

        end_time = time.time()
        total_fine_tuning_time = end_time - start_time
        
        training_details = f"Fine-tuning terminé! Temps total: {total_fine_tuning_time:.2f} secondes | {total_fine_tuning_time/60:.2f} min | {total_fine_tuning_time/3600:.2f} hours"
        print(training_details)

        # Enregistrer le modèle finetuné
        self.model.save_pretrained(model_save_path)
        print(f"Modèle enregistré à {model_save_path}")
        
        with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([training_details])
            csv_writer.writerow([f"Modèle enregistré à {model_save_path}"])


    def predict(self, text):
        inputs = self.preprocess([text])
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predictions = predictions.cpu().detach().numpy()
        predictions = np.argmax(predictions)
        return predictions

    def predict_label_links(self, cleaned_links):
        link_name_label = []
        for i in range(len(cleaned_links)):
            predictions = self.predict(cleaned_links[i][1])
            link_name_label.append((cleaned_links[i][0], cleaned_links[i][1], predictions))
        return link_name_label
        
    def get_contact_links(self, htmlContent):
        links = self.linkProcessing.preprocess_links(htmlContent)
        predictedLinks = self.predict_label_links(links)
        return [link[:2] for link in predictedLinks if link[2]==1]