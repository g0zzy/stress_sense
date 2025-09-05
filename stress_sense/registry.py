## all functions related to load / save model

import os # to get the env variables
from sklearn.pipeline import Pipeline
import pickle



def load_model(model_name="Production") -> Pipeline:
    """
    Return a saved model:
    - locally (given by MODEL_NAME environment variable) if MODEL_TARGET=='local'  -->
    - or from GCS (most recent one) if MODEL_TARGET=='gcs'  -->

    Return None (but do not Raise) if no model is found

    """
    # print(model_name)
    # return
    MODEL_TARGET = (os.environ.get('MODEL_TARGET')) # local or gcp

    if MODEL_TARGET == "local":
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'models')
        # local_model_paths
        print(f"\nLoad model from local registry...\n{path}\n")
        print(f"Model name : {model_name}")
        file = os.path.join(path,model_name)

        if not os.path.isfile(file):
            print(f"\n❌ No model found in {BUCKET_NAME} with the name {model_name}")
            return None

        with open(file,'rb') as f:
            model = pickle.load(f)

        print("✅ Model loaded from local disk")
        return model

    '''
    elif MODEL_TARGET == "gcs":
        # 🎁 We give you this piece of code as a gift. Please read it carefully! Add a breakpoint if needed!
        print(Fore.BLUE + f"\nLoad latest model from GCS..." + Style.RESET_ALL)

        client = storage.Client()
        blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="model"))

        try:
            latest_blob = max(blobs, key=lambda x: x.updated)
            latest_model_path_to_save = os.path.join(LOCAL_REGISTRY_PATH, latest_blob.name)
            latest_blob.download_to_filename(latest_model_path_to_save)

            latest_model = keras.models.load_model(latest_model_path_to_save)

            print("✅ Latest model downloaded from cloud storage")

            return latest_model
        except:
            print(f"\n❌ No model found in GCS bucket {BUCKET_NAME}")

            return None

    elif MODEL_TARGET == "mlflow":
        print(Fore.BLUE + f"\nLoad [{stage}] model from MLflow..." + Style.RESET_ALL)

        # Load model from MLflow
        model = None
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = MlflowClient()

        try:
            model_versions = client.get_latest_versions(name=MLFLOW_MODEL_NAME, stages=[stage])
            model_uri = model_versions[0].source

            assert model_uri is not None
        except:
            print(f"\n❌ No model found with name {MLFLOW_MODEL_NAME} in stage {stage}")

            return None

        model = mlflow.tensorflow.load_model(model_uri=model_uri)

        print("✅ Model loaded from MLflow")
        return model
    else:
        return None
'''
