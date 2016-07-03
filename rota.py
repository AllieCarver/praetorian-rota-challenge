import requests


class RotaAPI:
    
    def __init__(self):
        self._base_url = 'http://rota.praetorian.com/rota/service/play.php'
        self._res = requests.get(self._base_url+"?request=new")
        self._cookies = self._res.cookies.get_dict()
        self.json = self._res.json()    
    def reset(self):
        self._res = requests.get(self._base_url+"?request=new")
        self._cookies = self._res.cookies.get_dict()
    
    def place(self, x):
        res = requests.get(self._base_url+"?request=place&location="+str(x), 
                           cookies = self._cookies)
        return res.json()

    def move(self, x, y):
        res = requests.get(self._base_url+"?request=move&from="+str(x)+"&to="+str(y), 
                           cookies = self._cookies)
        return res.json()   

    def status(self):
        res = requests.get(self._base_url+"?request=status", 
                           cookies = self._cookies)
        return res.json()                            