from app.models.company import Company
from app.repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def list_companies(self):
        return self.company_repository.get_companies()

    def list_company_maped(self):
        return self.company_repository.get_companies_map()

    def get_profile(self, company_id: int):
        return self.company_repository.get_company_by_id(company_id)

    def create_company(self, company_data: Company):
        return self.company_repository.create_company(company_data)

    def update_stack(self, company_id: int, stack_data):
        return self.company_repository.update_stack(company_id, stack_data)

    def delete_company(self, company_id: int):
        return self.company_repository.delete_company(company_id)
