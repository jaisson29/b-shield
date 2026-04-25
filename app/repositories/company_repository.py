from app.models.company import Company


class CompanyRepository:
    def __init__(self, db):
        self.db = db

    def get_company_by_id(self, company_id):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def create_company(self, company_data):
        new_company = Company(**company_data)
        self.db.add(new_company)
        self.db.commit()
        self.db.refresh(new_company)
        return new_company

    def update_company(self, company_id, company_data):
        company = self.get_company_by_id(company_id)
        if not company:
            return None
        for key, value in company_data.items():
            setattr(company, key, value)
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete_company(self, company_id):
        company = self.get_company_by_id(company_id)
        if not company:
            return None
        self.db.delete(company)
        self.db.commit()
        return company
