# 308 lines --> ___ lines
import numpy as np
from sklearn.base import BaseEstimator


def entropy(y):  
    """
    Computes entropy of the provided distribution. Use log(value + eps) for numerical stability
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset
    
    Returns
    -------
    float
        Entropy of the provided subset
    """
    EPS = 0.0005

    # YOUR CODE HERE
    if len(y) == 0:
        return 0.0
    probs = y.mean(axis=0)
    result = -(probs * np.log2(probs + EPS)).sum()
    return result # 0.
    
def gini(y):
    """
    Computes the Gini impurity of the provided distribution
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, n_classes)
        One-hot representation of class labels for corresponding subset
    
    Returns
    -------
    float
        Gini impurity of the provided subset
    """

    # YOUR CODE HERE
    if len(y) == 0:
        return 0.0
    probs = y.mean(axis=0)
    result = 1 - (probs ** 2).sum()
    return result # 0.
    
def variance(y):
    """
    Computes the variance the provided target values subset
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector
    
    Returns
    -------
    float
        Variance of the provided target vector
    """
    
    # YOUR CODE HERE
    if len(y) == 0:
        return 0.0
    m = y.mean()
    result = ((y - m)**2).mean()
    return result # 0.

def mad_median(y):
    """
    Computes the mean absolute deviation from the median in the
    provided target values subset
    
    Parameters
    ----------
    y : np.array of type float with shape (n_objects, 1)
        Target values vector
    
    Returns
    -------
    float
        Mean absolute deviation from the median in the provided vector
    """

    # YOUR CODE HERE
    if len(y) == 0:
        return 0.0
    med = np.median(y)
    result = (abs(y - med)).mean()
    return result # 0.


def one_hot_encode(n_classes, y):
    y_one_hot = np.zeros((len(y), n_classes), dtype=float)
    y_one_hot[np.arange(len(y)), y.astype(int)[:, 0]] = 1.
    return y_one_hot


def one_hot_decode(y_one_hot):
    return y_one_hot.argmax(axis=1)[:, None]


class Node:
    """
    This class is provided "as is" and it is not mandatory to it use in your code.
    """
    def __init__(self, feature_index, threshold, proba=0):
        self.feature_index = feature_index
        self.threshold = threshold
        self.proba = proba
        self.mean = None # for regression
        self.left_child = None
        self.right_child = None
        
        
class DecisionTree(BaseEstimator):
    all_criterions = {
        'gini': (gini, True), # (criterion, classification flag)
        'entropy': (entropy, True),
        'variance': (variance, False),
        'mad_median': (mad_median, False)
    }

    def __init__(self, n_classes=None, max_depth=np.inf, min_samples_split=2, 
                 criterion_name='gini', debug=False):

        assert criterion_name in self.all_criterions.keys(), \
                'Criterion name must be one of the following: {}'.format(self.all_criterions.keys())
        
        self.n_classes = n_classes
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion_name = criterion_name

        self.depth = 0
        self.root = None # Use the Node class to initialize it later
        self.debug = debug

        
        
    def make_split(self, feature_index, threshold, X_subset, y_subset):
        """
        Makes split of the provided data subset and target values using provided feature and threshold
        
        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset
        
        Returns
        -------
        (X_left, y_left) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j < threshold
        (X_right, y_right) : tuple of np.arrays of same type as input X_subset and y_subset
            Part of the providev subset where selected feature x^j >= threshold
        """

        # YOUR CODE HERE
        mask_left = X_subset[:, feature_index] < threshold
        mask_right = X_subset[:, feature_index] >= threshold
        X_left, y_left = X_subset[mask_left], y_subset[mask_left]
        X_right, y_right = X_subset[mask_right], y_subset[mask_right]
        return (X_left, y_left), (X_right, y_right)
    
    def make_split_only_y(self, feature_index, threshold, X_subset, y_subset):
        """
        Split only target values into two subsets with specified feature and threshold
        
        Parameters
        ----------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels for corresponding subset
        
        Returns
        -------
        y_left : np.array of type float with shape (n_objects_left, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j < threshold

        y_right : np.array of type float with shape (n_objects_right, n_classes) in classification 
                   (n_objects, 1) in regression 
            Part of the provided subset where selected feature x^j >= threshold
        """

        # YOUR CODE HERE
        mask_left = X_subset[:, feature_index] < threshold
        mask_right = X_subset[:, feature_index] >= threshold
        y_left, y_right = y_subset[mask_left], y_subset[mask_right]
        return y_left, y_right

    def choose_best_split(self, X_subset, y_subset):
        """
        Greedily select the best feature and best threshold w.r.t. selected criterion
        
        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset
        
        Returns
        -------
        feature_index : int
            Index of feature to make split with

        threshold : float
            Threshold value to perform split

        """
        # YOUR CODE HERE
        crit = self.criterion        
        feature_index, threshold, min_impurity = 0, X_subset[:, 0].min(), np.inf
        
        for j in range(X_subset.shape[1]):
            all_t = np.unique(X_subset[:, j])
            for t in all_t:
                y_l, y_r = self.make_split_only_y(j, t, X_subset, y_subset)
                l_frac, r_frac = len(y_l) / len(y_subset), len(y_r) / len(y_subset)
                cur_impurity = crit(y_l) * l_frac + crit(y_r) * r_frac
                if cur_impurity < min_impurity:
                    feature_index = j
                    threshold = t
                    min_impurity = cur_impurity
        return feature_index, threshold
    
    def make_tree(self, X_subset, y_subset, cur_depth):
        """
        Recursively builds the tree
        
        Parameters
        ----------
        X_subset : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the selected subset

        y_subset : np.array of type float with shape (n_objects, n_classes) in classification 
                   (n_objects, 1) in regression 
            One-hot representation of class labels or target values for corresponding subset
        
        Returns
        -------
        root_node : Node class instance
            Node of the root of the fitted tree
        """

        # YOUR CODE HERE

        if X_subset.shape[0] > self.min_samples_split and cur_depth < self.max_depth: 
            f, t = self.choose_best_split(X_subset, y_subset)
            new_node = Node(f, t)
            (X_l, y_l), (X_r, y_r) = self.make_split(f, t, X_subset, y_subset)
            new_node.left_child = self.make_tree(X_l, y_l, cur_depth + 1)
            new_node.right_child = self.make_tree(X_r, y_r, cur_depth + 1)
        else:
            new_node = Node(-1, None)
            if self.classification:
                new_node.proba = np.mean(y_subset, axis=0)
            else:
                new_node.mean = np.mean(y_subset, axis=0)
        return new_node
        
    def fit(self, X, y):
        """
        Fit the model from scratch using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data to train on

        y : np.array of type int with shape (n_objects, 1) in classification 
                   of type float with shape (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression
        
        """
        # assert len(y.shape) == 2 and len(y) == len(X), 'Wrong y shape'
        
        self.criterion, self.classification = self.all_criterions[self.criterion_name]
        if self.classification:
            if self.n_classes is None:
                self.n_classes = len(np.unique(y))
            y = one_hot_encode(self.n_classes, y)
        self.root = self.make_tree(X, y, 0)
    
    def predict(self, X):
        """
        Predict the target value or class label  the model from scratch using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted : np.array of type int with shape (n_objects, 1) in classification 
                   (n_objects, 1) in regression 
            Column vector of class labels in classification or target values in regression
        
        """

        # YOUR CODE HERE
        y_predicted = np.zeros((len(X), 1))
        for i in range(len(X)):
            node = self.root
            while node.feature_index != -1:
                f, t = node.feature_index, node.threshold
                if X[i, f] < t:
                    node = node.left_child
                else:
                    node = node.right_child
            if self.classification:
                y_predicted[i] = np.argmax(node.proba)
            else:
                y_predicted[i] = node.mean
        return y_predicted
        
    def predict_proba(self, X):
        """
        Only for classification
        Predict the class probabilities using the provided data
        
        Parameters
        ----------
        X : np.array of type float with shape (n_objects, n_features)
            Feature matrix representing the data the predictions should be provided for

        Returns
        -------
        y_predicted_probs : np.array of type float with shape (n_objects, n_classes)
            Probabilities of each class for the provided objects
        
        """
        assert self.classification, 'Available only for classification problem'

        # YOUR CODE HERE
        y_predicted_probs = np.zeros((X.shape[0], self.n_classes))
        for i in range(len(X)):
            node = self.root
            while node.feature_index != -1:
                f, t = node.feature_index, node.threshold
                if X[i, f] < t:
                    node = node.left_child
                else:
                    node = node.right_child
            y_predicted_probs[i, :] = node.proba
        return y_predicted_probs
