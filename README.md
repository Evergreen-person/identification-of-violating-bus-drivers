# identification-of-violating-bus-drivers


# Quick start
0. Intall requirements<br>
```
pip install -r requirements.txt
```
1. Download model https://drive.google.com/drive/folders/1CDK3EChjnUAHcbCuFcZ8SMOfiWjwDqiD?usp=sharing
and specify the path to the model in the conf file in identification-of-violating-bus-drivers/configs/app_config.json field - model_filename
2. run code<br>
```
$ cd identification-of-violating-bus-drivers
$ python main.py --input "YOUR_VIDEO"\
                 --output "PATH_TO_SAVE"\
                 --config "config/app_config.json"
``` 