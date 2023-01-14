curl -X 'POST' \
  'http://localhost:3000/api/v1/user/repos' \
  -H 'accept: application/json' \
  -H 'authorization: Basic bWRjYWRtaW46cGFzc3dvcmQ=' \
  -H 'Content-Type: application/json' \
  -d '{
  "auto_init": false,
  "default_branch": "main",
  "description": "demo",
  "name": "repo-test",
  "private": false,
  "template": false,
  "trust_model": "default"
}'


cd tests/repo-test
git init
git add .
git checkout -b main
git commit -m "first commit"
git remote add origin "http://mdcadmin:password@localhost:3000/mdcadmin/repo-test"
git push -u origin main
