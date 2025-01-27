import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences

class StudentMovementLSTM:
    def __init__(self, input_shape=(None, 4)):
        self.model = self.build_model(input_shape)
    
    def build_model(self, input_shape):
        model = Sequential([
            LSTM(64, input_shape=input_shape, return_sequences=True),
            Dropout(0.3),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def prepare_movement_sequences(self, movement_data):
        """
        Prepare movement sequences for LSTM training
        Movement data format: [x, y, timestamp, location_type]
        """
        # Normalize movement features
        normalized_data = self.normalize_movements(movement_data)
        
        # Pad sequences to consistent length
        padded_sequences = pad_sequences(
            normalized_data, 
            padding='post', 
            dtype='float32'
        )
        
        return padded_sequences
    
    def normalize_movements(self, movements):
        """Normalize movement features"""
        normalized = []
        for sequence in movements:
            seq_normalized = []
            for movement in sequence:
                # Normalize x, y coordinates
                normalized_movement = [
                    movement[0] / 1920,  # Normalize x (assuming 1920 pixel width)
                    movement[1] / 1080,  # Normalize y (assuming 1080 pixel height)
                    movement[2],         # Timestamp
                    movement[3]          # Location type (encoded)
                ]
                seq_normalized.append(normalized_movement)
            normalized.append(seq_normalized)
        
        return normalized
    
    def train(self, movement_sequences, labels, epochs=50, batch_size=32):
        """Train LSTM on movement sequences"""
        X = self.prepare_movement_sequences(movement_sequences)
        y = np.array(labels)
        
        history = self.model.fit(
            X, y, 
            epochs=epochs, 
            batch_size=batch_size,
            validation_split=0.2
        )
        
        return history
    
    def predict_truancy(self, movement_sequence):
        """Predict truancy probability for a movement sequence"""
        processed_sequence = self.prepare_movement_sequences([movement_sequence])
        truancy_prob = self.model.predict(processed_sequence)
        return truancy_prob[0][0]
    
    def save_model(self, filepath='student_movement_lstm.h5'):
        """Save trained model"""
        self.model.save(filepath)
    
    def load_model(self, filepath='student_movement_lstm.h5'):
        """Load pre-trained model"""
        self.model = tf.keras.models.load_model(filepath)

# Example usage
lstm_model = StudentMovementLSTM()

# Synthetic training data
movement_sequences = [
    # Sequence of student movements: [x, y, timestamp, location_type]
    [[100, 200, 1.0, 0], [150, 250, 1.5, 1], [200, 300, 2.0, 2]],
    [[500, 600, 1.0, 0], [550, 650, 1.5, 0], [600, 700, 2.0, 0]]
]
labels = [1, 0]  # 1 for truancy, 0 for normal movement

# Train the model
lstm_model.train(movement_sequences, labels)

# Save the trained model
lstm_model.save_model()