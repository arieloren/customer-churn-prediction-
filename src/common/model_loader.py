import pickle
from sklearn.ensemble import RandomForestClassifier


class TransformModel():
    def __init__(self, config):
        self.config = config
        self.__load_dependency()

    def __validation(self, dataset):
        pass

    def __load_dependency(self):
        with open(self.config.MODEL_PATH, 'rb') as f:
            self.model: RandomForestClassifier = pickle.load(f)

    def predict_proba(self, dataset):
        dataset = dataset.loc[:, self.model.feature_names_in_]
        return self.model.predict_proba(dataset)

    def predict(self, dataset):
        self.__validation(dataset)
        # Enforce column order and names from the trained model
        dataset = dataset.loc[:, self.model.feature_names_in_]

        result = self.model.predict(dataset)
        return result
