Example Deployment using argocd
---

Setup Mlflow and Mlflow controllers for different stages using argocd

```
kubectl apply -f  argo-manifest
```

Log a Mlflow model with Seldon deployment configuration with the name deploy.yaml

<img width="783" alt="Screenshot 2022-07-10 at 6 26 01 PM" src="https://user-images.githubusercontent.com/62284209/178153282-9c107398-9f9f-4fc3-8bfc-ca9d5c9a9f3a.png">

<img width="1409" alt="Screenshot 2022-07-10 at 6 25 47 PM" src="https://user-images.githubusercontent.com/62284209/178153272-ae254b27-47ed-4251-aa69-07a305223aee.png">


Mlflow controllers will deploy the models to appropriate Namespaces based on the configuration

<img width="1038" alt="Screenshot 2022-07-10 at 6 27 11 PM" src="https://user-images.githubusercontent.com/62284209/178153334-8909cecb-162e-4f86-ac22-f6cff0a7859d.png">
