import numpy as np

class ZScoreDetector:

    def __init__(self) -> None:
        self.window = np.array([])
    
    # Function to detect anomalies using Z-Score
    def detect_anomaly( self, data_point) -> bool:
        
        self.window = np.append( self.window, data_point )

        if len(self.window) < 10:
            return False  # Not enough data for anomaly detection
        
        mean = np.mean( self.window)
        std_dev = np.std( self.window )
        
        if std_dev == 0:  # Avoid division by zero
            return False
        
        z_score = (data_point - mean) / std_dev
        return abs(z_score) > 3.5
    
    def reset( self ):
        self.window = np.array([])