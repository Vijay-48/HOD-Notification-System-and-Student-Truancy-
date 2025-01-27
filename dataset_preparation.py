import os
import cv2
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

class StudentDataset(Dataset):
    def __init__(self, image_dir, label_dir, transform=None):
        self.image_dir = image_dir
        self.label_dir = label_dir
        self.transform = transform
        self.images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
        
    def __len__(self):
        return len(self.images)
        
    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.images[idx])
        label_path = os.path.join(self.label_dir, 
                                 self.images[idx].replace('.jpg', '.txt'))
        
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        with open(label_path, 'r') as f:
            labels = np.array([x.split() for x in f.read().strip().splitlines()],
                            dtype=np.float32)
        
        if self.transform:
            augmentations = self.transform(image=image, bboxes=labels[:, 1:])
            image = augmentations["image"]
            labels = augmentations["bboxes"]
        
        return image, labels