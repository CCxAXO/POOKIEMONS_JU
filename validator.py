from typing import Dict, List
import uuid
from time import time

class CompanyValidator:
    def __init__(self):
        self.pending_applications: Dict[str, Dict] = {}
        self.verified_companies: Dict[str, Dict] = {}
        self.rejected_companies: Dict[str, Dict] = {}
        
        # Validation criteria weights
        self.criteria_weights = {
            'registration_docs': 0.3,
            'emission_reports': 0.25,
            'financial_status': 0.2,
            'iot_infrastructure': 0.15,
            'reputation_score': 0.1
        }
    
    def submit_application(self, company_data: Dict) -> str:
        """Submit company application for verification"""
        app_id = str(uuid.uuid4())
        
        application = {
            'application_id': app_id,
            'company_name': company_data['company_name'],
            'industry_type': company_data['industry_type'],
            'company_scale': company_data['company_scale'],
            'registration_number': company_data.get('registration_number'),
            'emission_baseline': company_data['emission_baseline'],
            'documents': company_data.get('documents', []),
            'submitted_at': time(),
            'status': 'pending',
            'validation_score': 0
        }
        
        self.pending_applications[app_id] = application
        print(f"Application submitted for {company_data['company_name']} - ID: {app_id}")
        return app_id
    
    def validate_company(self, app_id: str, criteria_scores: Dict[str, float]) -> bool:
        """Validate company based on criteria scores (0-100)"""
        if app_id not in self.pending_applications:
            raise ValueError("Application not found")
        
        application = self.pending_applications[app_id]
        
        # Calculate weighted validation score
        total_score = 0
        for criterion, weight in self.criteria_weights.items():
            score = criteria_scores.get(criterion, 0)
            total_score += (score / 100) * weight
        
        validation_score = total_score * 100
        application['validation_score'] = validation_score
        
        # Threshold for verification: 70%
        if validation_score >= 70:
            application['status'] = 'verified'
            application['verified_at'] = time()
            self.verified_companies[app_id] = application
            del self.pending_applications[app_id]
            print(f"✓ Company {application['company_name']} verified with score {validation_score:.2f}")
            return True
        else:
            application['status'] = 'rejected'
            application['rejected_at'] = time()
            application['rejection_reason'] = f"Validation score {validation_score:.2f} below threshold (70)"
            self.rejected_companies[app_id] = application
            del self.pending_applications[app_id]
            print(f"✗ Company {application['company_name']} rejected - Score: {validation_score:.2f}")
            return False
    
    def is_verified(self, company_name: str) -> bool:
        """Check if company is verified"""
        for app in self.verified_companies.values():
            if app['company_name'] == company_name:
                return True
        return False
    
    def get_company_info(self, company_name: str) -> Dict:
        """Get verified company information"""
        for app in self.verified_companies.values():
            if app['company_name'] == company_name:
                return app
        return None
    
    def auto_validate_demo(self, app_id: str) -> bool:
        """Auto-validate for demo purposes"""
        mock_scores = {
            'registration_docs': 85,
            'emission_reports': 80,
            'financial_status': 75,
            'iot_infrastructure': 70,
            'reputation_score': 90
        }
        return self.validate_company(app_id, mock_scores)