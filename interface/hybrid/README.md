# Hybrid

To run the hybrid model we need to build a container network on docker because of the different python requirments for Foofah framework and GPT

## LLM on Docker
Build LLM container and initialize the network
```sh
$ cd hybrid
$ docker network create mynetwork
$ docker build -t llm-container -f llm.Dockerfile .
$ docker run -d --name container1  --network mynetwork -p 5050:5050 llm-container
```

## Foofah on Docker

Build Foofah container
```sh
$ docker build -t foofah-container -f foofah.Dockerfile .
```

## Start contrainers

```sh
$ docker run --rm --name container2  --network mynetwork foofah-container
$ docker run -d --name container2 --network mynetwork foofah-container
```
Foofah web service will be available at [localhost:8080](http://0.0.0.0:8080).

## Test Hybrid Model on Docker 

First copy the enitre data folder in the root directory under the tests folder in hybrid folder
```sh
$ chmod +x run.sh 
$ ./run.sh tests/data/prose (or foofah)
```


## Acknowledgements
Foofah is being developed in the University of Michigan. This work in part supported by National Science Foundation grants IIS-1250880, IIS-1054913, NSF IGERT grant 0903629,
a Sloan Research Fellowship and a CSE Department Fellowship

## References
[1] [ "Foofah: Transforming Data By Example", SIGMOD 17',
Zhongjun Jin, Michael R. Anderson, Michael Cafarella, H. V. Jagadish](http://dl.acm.org/authorize?N37756)

[2] ["Foofah: A Programming-By-Example System for Synthesizing Data Transformation Programs", SIGMOD 17', Demo,
Zhongjun Jin, Michael R. Anderson, Michael Cafarella, H. V. Jagadish](http://dl.acm.org/authorize?N37718)

[3] ["Potter's wheel: An interactive data cleaning system." VLDB. Vol. 1. 2001.
Raman, Vijayshankar, and Joseph M. Hellerstein.  ](http://www.vldb.org/conf/2001/P381.pdf)