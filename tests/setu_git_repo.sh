cd test/repo-test
git init
git add .
git checkout -b main
git commit -m "first commit"
git remote add origin "http://mdcadmin:password@localhost:3000/mdcadmin/repo-test"
git push -u origin main
