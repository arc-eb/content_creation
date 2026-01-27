"""
Database models for Bompard content creation tool.
Tracks generation history, AI models, and user sessions.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Generation(db.Model):
    """Store generation history for garment swaps and AI models."""
    __tablename__ = 'generations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Generation type: 'garment_swap' or 'ai_model'
    generation_type = db.Column(db.String(20), nullable=False, index=True)
    
    # File paths
    model_image_path = db.Column(db.String(255))
    flatlay_image_path = db.Column(db.String(255))
    output_image_path = db.Column(db.String(255), nullable=False)
    
    # Settings used
    custom_instructions = db.Column(db.Text)
    refinements = db.Column(db.Text)
    output_size = db.Column(db.String(20))
    prompt_used = db.Column(db.Text)
    
    # Result metadata
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text)
    
    # Processing time
    processing_time_seconds = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Generation {self.id} - {self.generation_type} - {self.session_id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'generation_type': self.generation_type,
            'model_image_path': self.model_image_path,
            'flatlay_image_path': self.flatlay_image_path,
            'output_image_path': self.output_image_path,
            'custom_instructions': self.custom_instructions,
            'refinements': self.refinements,
            'output_size': self.output_size,
            'success': self.success,
            'error_message': self.error_message,
            'processing_time_seconds': self.processing_time_seconds
        }


class GeneratedImage(db.Model):
    """Store saved result images as binary data."""
    __tablename__ = 'generated_image'
    
    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<GeneratedImage {self.id} - {self.created_at}>'
    
    def to_dict(self, include_data=False):
        """Convert to dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'size_bytes': len(self.image_data) if self.image_data else 0
        }
        if include_data:
            import base64
            result['image_data'] = base64.b64encode(self.image_data).decode('utf-8')
        return result
