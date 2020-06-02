# identification-of-violating-bus-drivers
<p>This project helps detect people getting on / off by public transport in the wrong place.<p>

It uses Faster-RCNN-ResNet100 model to detect buses and people and uses [Deep SORT](https://github.com/nwojke/deep_sort) to track them. Test data and examples of the algorithm can be found [here](https://drive.google.com/drive/folders/1dPLL22fsZxqh5RvLVleDI1uRTjIyeQ9J?usp=sharing).

# Quick start
0. Intall requirements<br>
```
pip install -r requirements.txt
```
1. Download [model](https://drive.google.com/drive/folders/1CDK3EChjnUAHcbCuFcZ8SMOfiWjwDqiD?usp=sharing)
and specify the path to the model in the conf file in identification-of-violating-bus-drivers/configs/app_config.json field - model_filename

2. Run code<br>
```
$ cd identification-of-violating-bus-drivers
$ python main.py --input "YOUR_VIDEO"\
                 --output "PATH_TO_SAVE"\
                 --config "config/app_config.json"
``` 

# Citation

Deep SORT
```
@inproceedings{Wojke2017simple,
  title={Simple Online and Realtime Tracking with a Deep Association Metric},
  author={Wojke, Nicolai and Bewley, Alex and Paulus, Dietrich},
  booktitle={2017 IEEE International Conference on Image Processing (ICIP)},
  year={2017},
  pages={3645--3649},
  organization={IEEE},
  doi={10.1109/ICIP.2017.8296962}
}
```
```
@inproceedings{Wojke2018deep,
  title={Deep Cosine Metric Learning for Person Re-identification},
  author={Wojke, Nicolai and Bewley, Alex},
  booktitle={2018 IEEE Winter Conference on Applications of Computer Vision (WACV)},
  year={2018},
  pages={748--756},
  organization={IEEE},
  doi={10.1109/WACV.2018.00087}
}
```
