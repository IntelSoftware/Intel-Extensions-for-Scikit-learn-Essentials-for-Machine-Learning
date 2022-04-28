from tqdm import tqdm

############################# Import dpctl ######################
import dpctl
##################################################################

def gallery(cases):
    elapsed_fit = {}  # dictionary to track the time elapsed for the fit method
    elapsed_predict = {}  # dictionary to track the time elapsed for the predict/transform method 
    # the parmeters for this algorithms and for generating the data will be in the next cell
    for name, case in tqdm(cases.items()):
        print("\nname: ", name)
        algorithm = case['algorithm']
        try:
            estimator = algorithm['estimator'](**algorithm['params'])
            data = case['data']
            x, y = data['generator'](**data['params'])
            x.astype(float)
            y.astype(float)
            ###################  Add code to get_devices, get_devices, select_gpu_device  ########
            for d in dpctl.get_devices():
                gpu_available = False
                for d in dpctl.get_devices():
                    if d.is_gpu:
                        gpu_device = dpctl.select_gpu_device()
                        gpu_available = True
                    else:
                        cpu_device = dpctl.select_cpu_device() 
            if gpu_available:
                print("GPU targeted: ", gpu_device)
            else:
                print("CPU targeted: ", cpu_device)
            ######################################################################################

            ############### Add code to convert x & y to dpctl.tensors x_device, y_device #########
            x_device = dpctl.tensor.from_numpy(x, usm_type = 'device', queue=dpctl.SyclQueue(gpu_device))
            y_device = dpctl.tensor.from_numpy(y, usm_type = 'device', queue=dpctl.SyclQueue(gpu_device))
            ######################################################################################

            if hasattr(estimator, 'fit_predict'):
                ###################### Modify code to fit  x_device, y_device ####################
                estimator.fit(x_device, y_device)
                ##################################################################################
                
                print("fit_predict section", name," fit")
                
                ###################### Modify code to predict  x_device, y_device ####################
                catch_device = estimator.fit_predict(x_device, y_device)
                ######################################################################################
                
                print("fit_predict section", name," fit_predict")   
                
                #######################################################################################
                ##### Since we will use the prediction to score accuracy metrics, we need to cast it ##
                predictedHost = dpctl.tensor.to_numpy(catch_device)
                #######################################################################################
                
                print("fit_predict section dpctl.tensor.to_numpy", name)
                print(predictedHost)  
            elif hasattr(estimator, 'predict'):
                estimator.fit(x_device, y_device)
                print("predict section", name, " fit")
                catch_device = estimator.predict(x_device)
                print("predict section", name, " predict")
                predictedHost = dpctl.tensor.to_numpy(catch_device)
                print("predict section dpctl.tensor.to_numpy", name)
                print(predictedHost)
#                 estimator.fit(x, y)
#                 print("predict section", name, " fit")
#                 catch_device = estimator.predict(x)
#                 print("predict section", name, " predict")
#                 predicted = dpctl.tensor.to_numpy(catch_device)
#                 print("predict section dpctl.tensor.to_numpy", name)
#                 print(predicted)
                             
        except Exception as e:
            print('A problem has occurred from the Problematic code:\n', e)
            print("Not Supported as Configured\n\n")
        

def get_cases():
    return {
    'Logistic Regression': {
        "algorithm": {
            'estimator': sklearn.linear_model.LogisticRegression,
            'params': {
                'random_state': 43,
                'max_iter': 300,
                'penalty': 'l2'
            }
        },
        "data": {
            'generator': sklearn.datasets.make_classification,
            'params':
            {
                'n_samples': 10000,
                'n_features': 40,
                'n_classes': 3,
                'n_informative': 5,
                'random_state': 43,
            }
        }
    },
    'KNN Classifier': {
        "algorithm": {
            'estimator': sklearn.neighbors.KNeighborsClassifier,
            'params': {
                'n_jobs': -1,
            }
        },
        "data": {
            'generator': sklearn.datasets.make_classification,
            'params':
            {
                'n_samples': 3500,
                'n_features': 30,
                'n_classes': 3,
                'n_informative': 3,
                'random_state': 43,
            }
        }
    },
    'KNN Regression': {
        "algorithm": {
            'estimator': sklearn.neighbors.KNeighborsRegressor,
            'params': {
                'n_neighbors': 10,
                'n_jobs': -1,
            }
        },
        "data": {
            'generator': sklearn.datasets.make_regression,
            'params':
            {
                'n_samples': 3500,
                'n_features': 30,
                'n_targets': 1,
                'random_state': 43,
            }
        }
    },
    'Linear Regression': {
        "algorithm": {
            'estimator': sklearn.linear_model.LinearRegression,
            'params': {
                'n_jobs': -1,
            }
        },
        "data": {
            'generator': sklearn.datasets.make_regression,
            'params':
            {
                'n_samples': 3000,
                'n_features': 100,
                'n_targets': 1,  
                'random_state': 43,
            }
        }
    },     
    'dbscan': {
            "algorithm": {
            'estimator': sklearn.cluster.DBSCAN,
            'params': {
                'eps': 10,
                'min_samples' :2
            }
        },
        "data": {
            'generator': sklearn.datasets.make_blobs,
            'params':
            {
                'n_samples': 3000,  
                'n_features': 30,
                'centers': 8,
                'random_state': 43,
            }
        }
    },
    'k_means_random': {
            "algorithm": {
            'estimator': sklearn.cluster.KMeans,
            'params': {
                'n_clusters': 3,
                'random_state' :0, 
                'init' : 'random',                
            }
        },
        "data": {
            'generator': sklearn.datasets.make_blobs,
            'params':
            {
                'n_samples': 3000,  
                'n_features': 30,
                'centers': 8,
                'random_state': 43,
            }
        }
    },          
}
from sklearn import metrics
from sklearnex import patch_sklearn
patch_sklearn()  # this will set parameters such that the stock version of sklearn will be called
import sklearn.svm, sklearn.datasets, sklearn.neighbors, sklearn.linear_model, sklearn.decomposition
cases = get_cases()  #case the algorithm/dataset pairs
gallery(cases)  # call the bench function to captures the elapsed time dictionaries
print('All Tests Good\n')