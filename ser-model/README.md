# SER bachelor model

This directory is a part of the [emotional-bachelor-thesis](https://github.com/wiktorgorczak/bachelor_thesis). 
Contains files regarding `SER model` implementation, training and deployment as an `Docker image` on `AWS Lambda`. It is possible to utilize separate parts of this directory. 

Directory `model` contains scripts creating model structure, preparing the datasets for training and the model training itself. 

Directory `data` represents dataset folder structure proposed by tensorflow module to utilize with `image_dataset_from_directory` function - used in this solution. In addition, there can be found `jupyter notebook` presenting the process of data retrieval and data processing applied on the original emotional speech databases. 

The whole solution was created to perform emotion recognition from speech recordings with cloud processing. Among two approaches taken, both are using AWS Lambda service, but in two models:
* as a regular single script `Lambda function` with usage of `Lambda Layers`
* as a `Docker image` launched by Lambda 

In first case, it is necessary to `create Lambda Layer` containing zip package being virtual environment with particular modules installed (detailed in `requirements.txt`) as the basic Lmabda instance does not provide them. Adding Layer with environment containing required modules, allows to import them in main function.

## Building image with pretrained model

**Before building** it, make sure, that pretrained model is saved in directory `ser-model/model` in `.tflight` format.
To build an image of this solution, changing current directory to `this one`, run the following command:

```bash 
path-to-folder/ser-model$ docker build -t <name-of-your-choice> .
```

This will build the docker `image containing` pretrained `model` and `script for Lambda function`.

### **WARNING** 
The size of the `image` is `exceeding the free usage of repository month limit (500MB)`, so make sure you can live with it...

For next steps of function deployment see the []() guides. 
