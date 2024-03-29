# -*- coding: utf-8 -*-
# """Copy of time_series.ipynb

# Automatically generated by Colaboratory.

# Original file is located at
#     https://colab.research.google.com/drive/14CNI4fWs4PjsNBNKQzsXKhgjMbvGVi_J
# """

##importing Streamlit package
import streamlit as st
##giving the title to stramlit project
st.title ('Current forecasting and feature effect')
##writing first command in streamlit
st.write('Importing the required python libraries')
##importing required libraries
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import pandas as pd
from sklearn import pipeline
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler, MinMaxScaler
st.write('Importing the required python libraries')
##defining the main function
def main():
    ##defining the file upload function when user open stramlit link(deployed in heroku)
    def upload():
        global df1
        uploaded_file=st.sidebar.file_uploader(label='upload your csv or excel file.' ,type=['csv','xlsx'])
        if uploaded_file is not None:
            st.write('Reading the uploaded file')
            df1=pd.read_csv(uploaded_file)
            df=df1.copy()
            st.write('printing first five rows of the data')
            st.dataframe(df.head())
            return df
         
    st.write('Importing the required python libraries') 
    st.write('printing first five rows of the data')
    st.dataframe(df.head())
    ##defining the columns function to selected columns
    def columns():
        col=['Timestamp','TR3 V313 AGITATOR AMPS','T3 ES RSD V313 S','TR3 RSC#A INLET TEMP','TR3 RSC#B INLET TEMP','TR3 RSC#C INLET TEMP']
        return col
    ##caling both columns and upload functions
    col=columns()
    df=upload()
    ##defing the copy1 function for selected columns and making timestamp as index
    def copy1(col,df):
        #df=data_upload()
        #col=columns()
        df=df[col]
        st.write('Printing the feature names for model building')
        st.write(df.columns)
        st.write('Data preprocessing')
        features = df
        features.index = df['Timestamp']
        features.drop(columns=['Timestamp'],inplace=True)
        return features
    ##calling the copy1 function
    features=copy1(col,df)
    ##defing the scaling function for data normalization
    def sacling(features):
        #features=copy1()
        scaler=pipeline.Pipeline(steps=[
          ('z-scale', StandardScaler()),
             ('minmax', MinMaxScaler(feature_range=(-1, 1))),
             ('remove_constant', VarianceThreshold())])
        df=scaler.fit_transform(features)
        return df



    def create_time_steps(length):
        return list(range(-length, 0))

    def show_plot(plot_data, delta, title):
        plt.rcParams['figure.figsize'] = (8, 6)
        plt.rcParams['axes.grid'] = False
        labels = ['History', 'True Future', 'Model Prediction']
        marker = ['.-', 'rx', 'go']
        time_steps = create_time_steps(plot_data[0].shape[0])
        if delta:
            future = delta
        else:
            future = 0

        plt.title(title)
        for i, x in enumerate(plot_data):
            if i:
                plt.plot(future, plot_data[i], marker[i], markersize=10,
                   label=labels[i])
            else:
                plt.plot(time_steps, plot_data[i].flatten(), marker[i], label=labels[i])
            plt.legend()
            plt.xlim([time_steps[0], (future+5)*2])
            plt.xlabel('Time-Step')
            return plt
    ##creating the 3d array(batch_size,lookback,features) for model input
    def multivariate_data(dataset, target, start_index, end_index, history_size,
                          target_size, step, single_step=False):
        data = []
        labels = []

        start_index = start_index + history_size
        if end_index is None:
            end_index = len(dataset) - target_size

        for i in range(start_index, end_index):
            indices = range(i-history_size, i, step)
            data.append(dataset[indices])

            if single_step:
                labels.append(target[i+target_size])
            else:
                labels.append(target[i:i+target_size])

        return np.array(data), np.array(labels)

    ##calling the scaling function
    df=sacling(features)
    ##defing the model_dev function for doing data spliting and model development
    def model_dev(df):
        #df=sacling()
        future_target = 10
        past_history=60
        TRAIN_SPLIT=100000
        STEP=1
        x_train_multi, y_train_multi = multivariate_data(df, df[:, 0], 0,
                                                         TRAIN_SPLIT, past_history,
                                                         future_target, STEP)
        x_val_multi, y_val_multi = multivariate_data(df, df[:, 0],
                                                     TRAIN_SPLIT,150000, past_history,
                                                     future_target, STEP)



        BATCH_SIZE=200
        BUFFER_SIZE=50
        train_data_multi = tf.data.Dataset.from_tensor_slices((x_train_multi, y_train_multi))
        train_data_multi = train_data_multi.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

        val_data_multi = tf.data.Dataset.from_tensor_slices((x_val_multi, y_val_multi))
        val_data_multi = val_data_multi.batch(BATCH_SIZE).repeat()
        st.write('Building the neural network flow')

        multi_step_model = tf.keras.models.Sequential()
        multi_step_model.add(tf.keras.layers.LSTM(5,
                                                  return_sequences=True,
                                                  input_shape=x_val_multi.shape[-2:],activation='relu', recurrent_activation='sigmoid'))
        multi_step_model.add(tf.keras.layers.BatchNormalization())
        multi_step_model.add(tf.keras.layers.Dropout(0.1))
        multi_step_model.add(tf.keras.layers.LSTM(5,return_sequences=True,
                                                  activation='tanh'
                                                   ))
        multi_step_model.add(tf.keras.layers.BatchNormalization())
        # multi_step_model.add(tf.keras.layers.Dropout(0.3))
        # multi_step_model.add(tf.keras.layers.LSTM(5,return_sequences=True,
        #                                           activation='tanh'
        #                                           ))
        # multi_step_model.add(tf.keras.layers.BatchNormalization())
        # multi_step_model.add(tf.keras.layers.Dropout(0.3))
        # multi_step_model.add(tf.keras.layers.LSTM(5,return_sequences=True,activation='tanh'))
        # multi_step_model.add(tf.keras.layers.LayerNormalization(axis=1 , center=True , scale=True))
        # multi_step_model.add(tf.keras.layers.LSTM(5,return_sequences=True,activation='tanh'))
        # multi_step_model.add(tf.keras.layers.BatchNormalization())
        multi_step_model.add(tf.keras.layers.LSTM(5, activation='relu'))
        multi_step_model.add(tf.keras.layers.Dense(10,activation='linear', kernel_regularizer=tf.keras.regularizers.l1(0.01)))
        adam=tf.keras.optimizers.Adam(learning_rate=0.04, beta_1=0.9, beta_2=0.99, epsilon=1e-03)
        multi_step_model.compile(optimizer='adam', loss='mae',metrics=['mae'])
        st.write('Weight updation through BP algorithm')
        #multi_step_model,x_val_multi,y_val_multi=model_dev()
        return multi_step_model ,x_val_multi,y_val_multi
   
    def multi_step_plot(history, true_future, prediction):
        plt.figure(figsize=(12, 6))
        num_in = create_time_steps(len(history))
        num_out = len(true_future)
        STEP=1
        plt.plot(num_in, np.array(history[:, 1]), label='History')
        plt.plot(np.arange(num_out)/STEP, np.array(true_future), 'bo',
               label='True Future')
        if prediction.any():
            plt.plot(np.arange(num_out)/STEP, np.array(prediction), 'ro',
                 label='Predicted Future')
        plt.legend(loc='upper left')
        plt.show()

    # from google.colab import drive
    # drive.mount('/content/gdrive')

    # """In this plot and subsequent similar plots, the history and the future data are sampled every hour."""

    # checkpoint_path =  "/content/gdrive/My Drive/savemodel/15mymode.h5"
    # checkpoint_dir = os.path.dirname(checkpoint_path)

    # # batch_size = 32

    # # # Create a callback that saves the model's weights every 5 epochs
    # cp_callback = tf.keras.callbacks.ModelCheckpoint(
    #     filepath=checkpoint_path, 
    #     verbose=1, 
    #     save_weights_only=True,
    #     save_best_only=True)

    # # # Save the weights using the `checkpoint_path` format
    # multi_step_model.save_weights(checkpoint_path.format(epoch=0))
    # EPOCHS=50
    # EVALUATION_INTERVAL=100
    # multi_step_1 = multi_step_model.fit(train_data_multi, epochs=EPOCHS,
    #                                           steps_per_epoch=EVALUATION_INTERVAL,
    #                                           validation_data=val_data_multi, validation_steps=50
    #                                            ,callbacks=cp_callback,verbose=1)

    # pyplot.plot(multi_step_model.history.history['loss'])
    # pyplot.plot(multi_step_model.history.history['val_loss'])
    # pyplot.title('model train vs validation loss')
    # pyplot.ylabel('loss')
    # pyplot.xlabel('epoch')
    # pyplot.legend(['train', 'validation'], loc='upper right')
    # pyplot.show()
    from sklearn.externals import joblib
    pip install shap
    # import shap
    #from matplotlib import pyplot as plt
    multi_step_model,x_val_multi,y_val_multi=model_dev(df)
    ##defing the model_predictions function check the perturbation effect
    def model_predictons( multi_step_model,x_val_multi,y_val_multi):
        k=0
        for j in range(1,10):
            k=k+1
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.write('forecasting the Amps values')
            #multi_step_model,x_val_multi,y_val_multi=model_dev()
            st.pyplot(multi_step_plot(x_val_multi[j],y_val_multi[j],multi_step_model.predict(x_val_multi)[j]))
            orig_out=multi_step_model.predict(x_val_multi)[j]
            st.write('Calculating the effect of each feature on model forecasting')
            for i in range(5):  # iterate over the three features
                new_x = x_val_multi[j:k+1].copy()
                perturbation = np.random.normal(0.0, 1, size=new_x.shape[:2 ])
                # print(perturbation[:, :i])
                new_x[:, :, i] = new_x[:, :, i] + perturbation
                perturbed_out = multi_step_model.predict(new_x)
                effect = ((orig_out - perturbed_out) ** 2).mean() ** 0.5
                st.write(f'Variable {i+1}, perturbation effect: {effect:.4f}')
    model_predictons( multi_step_model,x_val_multi,y_val_multi) 
                
    
##calling the main function 
if __name__ == '__main__':
    main()

