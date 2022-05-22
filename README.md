# Face Mask

Application used to mask faces base on uploaed image.

# Technology
* Python: 3.7
* Flask
* libraries like pandas, numpy

## Configuration
* 1. create a virtual environment:
    ```
    conda create -n facemask python=3.7
    ```

* 2. activate newly created environment:
    ```
    conda activate facemask
    ```

* 3. In the virtual environment, Go to the project root folder and run below command to install packages:
    ```
    pip install -r requirements.txt  
    ```

     If any packages fail to install, try installing individually
     If any errors, try to do this one more time to avoid packages being missed out

* 4. Create Tables (optional)
    ```python
    python create_table.py
    ```

## Start web application
```python
python main.py --ip 127.0.0.1 --port 8000
```
## References
*  Ageitgey, (2022 Mar 10). Face Recognition. Retrieved from https://github.com/ageitgey/face_recognition 
 
*  Cardano-max, (2022 Apr 04). Find faces in pictures. Retrieved from https://deepnote.com/@cardano-max/Face-Recognition-1c4ca171-5e58-4d2c-b6a9-7904402a65c0
 
*  Mohammed Maheer, (2022 Apr 04). Face Recognition Using ‘face_recognition’ API. Retrieved from https://medium.com/analytics-vidhya/face-recognition-using-face-recognition-api-e7fa4dcabbc3
 
*  Vimsky.com, (2022 Apr 04). Python face_recognition.compare_faces. Retrieved from https://vimsky.com/zh-tw/examples/detail/python-method-face_recognition.compare_faces.html


