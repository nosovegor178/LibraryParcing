import requests
import os


directory = 'Books'

def get_N_number_of_books(N):
    for i in list(range(1, N+1)):
        url = "https://tululu.org/txt.php?id={}".format(i)

        response = requests.get(url)
        response.raise_for_status() 

        filename = 'id{}.txt'.format(i)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open('{}/{}'.format(directory,filename), 'wb') as file:
            file.write(response.content)


get_N_number_of_books(10)