initialize_git:
	@echo "initialization ..."
	git init
	git add .
	git commit -m "My first commit"
	git branch -M main
	git remote add origin https://github.com/EDJINEDJA/icd10-db-4-icd10taskclassification.git
	git push -u origin main
	
pip_git:
	@echo "pushing ..."
	git add .
	git commit -m "commit"
	git push -u origin main
	

setup: initialize_git
run: pip_git
