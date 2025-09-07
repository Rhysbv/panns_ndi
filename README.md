# panns_ndi


# Installation
This demo uses docker, instructions on how to install docker onto your machine can be found [here](https://docs.docker.com/get-started/introduction/get-docker-desktop/)

You will also need an NDI source. The easiest way to achieve this is [OBS](https://obsproject.com/) with the [DistroAV plugin](https://github.com/DistroAV/DistroAV). You will also need to install the NDI runtime. This can be done by installing [NDI Tools](https://ndi.video/tools/) on Windows and Mac or the [NDI SDK](https://ndi.video/for-developers/ndi-sdk/) on Linux. 

For the containers to see our NDI source, we must set the address of the discovery server. If running the containers on the same machine as the NDI source, we can set it to localhost. On Windows and Mac this can be done in NDI Tools -> Access Manager -> Advanced. See [here](https://docs.ndi.video/all/getting-started/white-paper/discovery-and-registration/discovery-server) for more details. On Linux this can be done manually by editing or creating the file ~/.ndi/ndi-config.v1.json containing:
```
{
    "ndi": {
        "networks": {
            "discovery": "discovery-service"
        }
    }
}
```

Once this is done, with the docker runtime running, type: `docker compose up --build`

This will begin to build all the required containers (beware this will take some time and disk space).

# Running the demo
With everything installed and running, we can start using the demo. To begin go to `http://localhost:5000` (prepare for some incredible UI). This is a frontend to the contaier running E-Panns. There should be a drop down menu conatining all the NDI sources on your network. Select one and click connect.
If this is the first time running the demo, it will now download the E-PANNs checkpoint which may take some time. Once this is done go to `http://localhost:5002` The current sound prediction should be displayed. An NDI source called "SED Output" can also be found, showing the source post processing. 



Prediction results and model latency with the associated latency computed on a AMD Ryzen 5 2500U and Intel Core i9-13900HX hardware:
# Prediction results:
predict_results.pdf
# model latency results
Latency.xlsx
