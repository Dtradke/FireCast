import time
from time import localtime, strftime
import os

print('importing keras...')
import tensorflow as tf
# import keras.models
# from keras.models import Sequential
# from keras.optimizers import SGD, RMSprop
# from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
# from keras.optimizers import SGD
# from keras.losses import mse, binary_crossentropy
# from keras.models import load_model
# from keras.callbacks import EarlyStopping
# from keras.layers import Dense, Activation, Dropout, Flatten, Concatenate, Input
# from keras.optimizers import SGD, RMSprop
# from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
import random
import numpy as np
print('done.')


try:
    from lib import preprocess
except:
    import preprocess

# class ImageBranch(Sequential):
#
#     def __init__(self, nchannels, kernelDiam):
#         super().__init__()
#         # there is also the starting perim which is implicitly gonna be included
#         nchannels += 1
#         input_shape = (kernelDiam, kernelDiam, nchannels)
#
#         self.add(AveragePooling2D(pool_size=(2,2), strides=(2,2), input_shape=input_shape))
#         self.add(Conv2D(32, kernel_size=(3,3), strides=(1,1),
#                         activation='sigmoid'))
#         self.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
#         self.add(Dropout(0.5))
#         self.add(Conv2D(64, (3,3), activation='relu'))
#         self.add(MaxPooling2D(pool_size=(2,2)))
#         self.add(Dropout(0.5))
#         self.add(Flatten())
#         self.add(Dense(128, activation='relu'))
#         self.add(Dropout(0.5))
#
#         self.compile(optimizer='rmsprop',
#             loss='binary_crossentropy',
#             metrics=['accuracy'])
#
# class BaseModel(object):
#
#     DEFAULT_EPOCHS = 1
#     DEFAULT_BATCHSIZE = 1000
#
#     def __init__(self, kerasModel=None, preProcessor=None):
#         self.kerasModel = kerasModel
#         self.preProcessor = preProcessor
#
#     def fit(self, trainingDataset, validatateDataset=None, epochs=DEFAULT_EPOCHS,batch_size=DEFAULT_BATCHSIZE):
#         assert self.kerasModel is not None, "You must set the kerasModel within a subclass"
#         assert self.preProcessor is not None, "You must set the preProcessor within a subclass"
#
#         print('training on ', trainingDataset)
#         # get the actual samples from the collection of points
#         (tinputs, toutputs), ptList = self.preProcessor.process(trainingDataset)
#         if validatateDataset is not None:
#             (vinputs, voutputs), ptList = self.preProcessor.process(validatateDataset)
#             history = self.kerasModel.fit(tinputs, toutputs, batch_size=batch_size, epochs=epochs, validation_data=(vinputs, voutputs))
#         else:
#             history = self.kerasModel.fit(tinputs, toutputs, batch_size=batch_size, epochs=epochs)
#         return history
#
#     def predict(self, dataset):
#         assert self.kerasModel is not None, "You must set the kerasModel within a subclass"
#         print("In predict")
#         (inputs, outputs), ptList = self.preProcessor.process(dataset)
#         results = self.kerasModel.predict(inputs).flatten()
#         if mode:
#             resultDict = {pt:random.utility(0.0, 1.0) for (pt, pred) in zip(ptList, results)}
#         else:
#             resultDict = {pt:pred for (pt, pred) in zip(ptList, results)}
#         return resultDict
#
#     def save(self, name=None):
#         if name is None:
#             name = strftime("%d%b%H_%M", localtime())
#         if "models/" not in name:
#             name = "models/" + name
#         if not name.endswith('/'):
#             name += '/'
#
#         if not os.path.isdir(name):
#             os.mkdir(name)
#
#         className = str(self.__class__.__name__)
#         with open(name+'class.txt', 'w') as f:
#             f.write(className)
#         self.kerasModel.save(name+'model.h5')

# def load(modelFolder):
#     if 'models/' not in modelFolder:
#         modelFolder = 'models/' + modelFolder
#     assert os.path.isdir(modelFolder), "{} is not a folder".format(modelFolder)
#
#     if not modelFolder.endswith('/'):
#         modelFolder += '/'
#
#     modelFile = modelFolder + 'model.h5'
#     model = keras.models.load_model(modelFile)
#
#     objFile = modelFolder + 'class.txt'
#     # print(objFile)
#     with open(objFile, 'r') as f:
#         classString = f.read().strip()
#     # print('classString is ', classString)
#     # print(globals())
#     class_ = globals()[classString]
#     obj = class_(kerasModel=model)
#     # print('done! returning', obj)
#     return obj



def fireCastModel(preProcessor, weightsFileName=None):
    if weightsFileName:
        fname = 'models/' + weightsFileName + ".h5"
        model = tf.keras.models.load_model(fname)
        return model


    kernelDiam = 2*preProcessor.AOIRadius+1
    nchannels = len(preProcessor.whichLayers) + 1
    wb = tf.keras.layers.Input((preProcessor.numWeatherInputs,),name='weatherInput')
    ib = tf.keras.layers.Input((kernelDiam, kernelDiam, nchannels),name='imageBranch')

    # print(">>>>weather: ", preProcessor.numWeatherInputs)
    # print(">>>>kernelDiam: ", kernelDiam, " chan: ", nchannels)

    avg_pool = tf.keras.layers.AveragePooling2D(pool_size=(2,2), strides=(2,2))(ib)
    conv1 = tf.keras.layers.Conv2D(32, kernel_size=(3,3), strides=(1,1), activation='sigmoid')(avg_pool)
    pool_1 = tf.keras.layers.MaxPooling2D(pool_size=(2,2), strides=(2,2))(conv1)
    d_1 = tf.keras.layers.Dropout(0.5)(pool_1)
    conv2 = tf.keras.layers.Conv2D(64, (3,3), activation='relu')(d_1)
    pool_2 = tf.keras.layers.MaxPooling2D(pool_size=(2,2))(conv2)
    d_2 = tf.keras.layers.Dropout(0.5)(pool_2)
    flat = tf.keras.layers.Flatten()(d_2)
    fc_1 = tf.keras.layers.Dense(128, activation='relu')(flat)
    d_3 = tf.keras.layers.Dropout(0.5)(fc_1)
    # --------

    concat = tf.keras.layers.Concatenate(name='mergedBranches')([wb,d_3]) #self.ib.output
    out = tf.keras.layers.Dense(1, kernel_initializer = 'normal', activation = 'sigmoid',name='output')(concat)
    # super().__init__([self.wb, self.ib.input], out)
    # super().__init__(inputs = [wb, ib], outputs = out)
    model = tf.keras.models.Model([wb, ib], out)

    # sgd = SGD(lr = 0.1, momentum = 0.9, decay = 0, nesterov = False)
    model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
    # sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    # model.compile(optimizer = sgd, loss = 'binary_crossentropy', metrics = ['accuracy'])

    return model


def fireCastFit(mod, preProcessor, training, validate, epochs=25):
    (tinputs, toutputs), ptList = preProcessor.process(training)
    (vinputs, voutputs), ptList = preProcessor.process(validate)
    # print('training on ', training)
    # history = super().fit(tinputs, toutputs, batch_size = 32, epochs=epochs, validation_data=(vinputs, voutputs))

    # es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=10)
    mod.fit(tinputs, toutputs, batch_size = 32, epochs=epochs, validation_data=(vinputs, voutputs)) #, callbacks=[es]

    # self.saveWeights()
    time_string = time.strftime("%Y%m%d-%H%M%S")
    fname = 'models/'+time_string + 'mod.h5'
    mod.save(fname)
    # return history

def fireCastPredict(mod, preProcessor, dataset, mode):
    print('start predict')
    (inputs, outputs), ptList = preProcessor.process(dataset)
    results = mod.predict(inputs).flatten()
    # for (p, pre) in zip(ptList, results):
    #     print(p)
    #     print(pre)
    if mode:
        resultDict = {pt:random.uniform(0.0,1.0) for (pt, pred) in zip(ptList, results)}
    else:
        resultDict = {pt:pred for (pt, pred) in zip(ptList, results)}
    print("end predict")
    return resultDict, results

#
# class FireModel(Model):
#
#     def __init__(self, preProcessor, weightsFileName=None):
#         self.preProcessor = preProcessor
#
#         kernelDiam = 2*self.preProcessor.AOIRadius+1
#         self.wb = Input((self.preProcessor.numWeatherInputs,),name='weatherInput')
#         self.ib = ImageBranch(len(self.preProcessor.whichLayers), kernelDiam)
#
#         concat = Concatenate(name='mergedBranches')([self.wb,self.ib.output])
#         out = Dense(1, kernel_initializer = 'normal', activation = 'sigmoid',name='output')(concat)
#         super().__init__([self.wb, self.ib.input], out)
#
#         sgd = SGD(lr = 0.1, momentum = 0.9, decay = 0, nesterov = False)
#         self.compile(loss = 'binary_crossentropy', optimizer = sgd, metrics = ['accuracy'])
#
#         if weightsFileName is not None:
#             self.load_weights(weightsFileName)
#
#     def fit(self, training, validate, epochs=1):
#         # get the actual samples from the collection of points
#         (tinputs, toutputs), ptList = self.preProcessor.process(training)
#         (vinputs, voutputs), ptList = self.preProcessor.process(validate)
#         # print('training on ', training)
#         print("inputs: ", tinputs[0].shape, " ----- ", tinputs[1].shape)
#         history = super().fit(tinputs, toutputs, batch_size = 32, epochs=epochs, validation_data=(vinputs, voutputs))
#
#         self.saveWeights()
#         return history
#
#     def saveWeights(self, fname=None):
#         if fname is None:
#             timeString = strftime("%d%b%H:%M", localtime())
#             fname = 'models/{}.h5'.format(timeString)
#         self.save_weights(fname)
#
#     def predict(self, dataset, mode):
#         print('start predict')
#         (inputs, outputs), ptList = self.preProcessor.process(dataset)
#         results = super().predict(inputs).flatten()
#         # for (p, pre) in zip(ptList, results):
#         #     print(p)
#         #     print(pre)
#         if mode:
#             resultDict = {pt:random.uniform(0.0,1.0) for (pt, pred) in zip(ptList, results)}
#         else:
#             resultDict = {pt:pred for (pt, pred) in zip(ptList, results)}
#         print("end predict")
#         return resultDict, results
#
# class OurModel(BaseModel):
#
#     def __init__(self, kerasModel=None):
#         numWeatherInputs = 8
#         usedLayers = ['dem','ndvi', 'aspect', 'band_2', 'band_3', 'band_4', 'band_5', 'slope']
#         AOIRadius = 30
#         pp = preprocess.PreProcessor(numWeatherInputs, usedLayers, AOIRadius)
#
#         if kerasModel is None:
#             kerasModel = self.createModel(pp)
#
#         super().__init__(kerasModel, pp)
#
#     @staticmethod
#     def createModel(pp):
#         # make our keras Model
#         kernelDiam = 2*pp.AOIRadius+1
#         wb = Input((pp.numWeatherInputs,),name='weatherInput')
#         ib = ImageBranch(len(pp.whichLayers), kernelDiam)
#
#         concat = Concatenate(name='mergedBranches')([wb,ib.output])
#         out = Dense(1, kernel_initializer = 'normal', activation = 'sigmoid',name='output')(concat)
#         kerasModel = Model([wb, ib.input], out)
#
#         sgd = SGD(lr = 0.1, momentum = 0.9, decay = 0, nesterov = False)
#         kerasModel.compile(loss = 'binary_crossentropy', optimizer = sgd, metrics = ['accuracy'])
#         return kerasModel
#
# class OurModel2(BaseModel):
#     pass
#
# if __name__ == '__main__':
#     m = OurModel()
#     m.save()
#
#     n = load('models/15Nov09_41')
#     print(n)
