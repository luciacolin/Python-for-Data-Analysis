# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 10:09:55 2022

@author: lulac
"""

#Definicion de librerias
import krakenex
from pykrakenapi import KrakenAPI
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd


class obtencion_de_datos:
    def __post_init__(self,moneda,fecha,nombre):
        self.moneda = moneda
        self.fecha = fecha
        self.nombre = nombre
       
    def conectarKrakenAPI(self):
        try:
            api = krakenex.API('api-key-1668535705986')
            k = KrakenAPI(api)

            data = k.get_asset_info()
            data=pd.DataFrame(data)
        except:
                print("No ha sido posible establecer la conexión")
        return k

    def getpairs(self):
        k=self.conectarKrakenAPI()
        pairs = k.get_tradable_asset_pairs()
        pairs.head().T
        pairs=pd.DataFrame(pairs)
        return pairs

    def sacardatos(self,moneda, fecha, nombre):
       try:
            d=fecha.split("-")
            for x in range(len(d)):
                d[x]=int(d[x])
            date_time_inicio=datetime.date(d[0],d[1],d[2])
            datex=date_time_inicio.timetuple()
            date_inicio=time.mktime(datex)
       except SyntaxError:
                    print("La fecha introducida no es valida y por tanto no se puede ejecutar la transformacion")
    
       conect=self.conectarKrakenAPI()
       datos = conect.get_ohlc_data(moneda, interval=1440, since=date_inicio, ascending = True)
       datos=datos[0]
       datos=pd.DataFrame(datos)
    
       x=nombre+'.csv'
    #guardara el archivo con los datos descargados en la carpeta en la que se esta trabajando
       datos.to_csv(x, header=True, index=False)
    
       return datos

    
class pintar_graficas:
    def __post_init__(self,datos):
        self.datos = datos


    def graficarmonedas(self,datos):
        fig, ax = plt.subplots()
        plt.title('ANÁLISIS DEL ' + moneda ,fontname='Times New Roman', fontweight='bold')
        plt.ylabel('Precio en euros',fontname='Times New Roman', fontweight='bold')
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.tick_params(axis='x', rotation=60)
        ax.set_facecolor("ivory")
   
        plt.plot(datos['open'],'teal',label='Apertura')
        plt.plot(datos['close'],'SteelBlue',label='Cierre')
        plt.plot(datos['high'],'springgreen',label='Máximo')
        plt.plot(datos['low'],'darkred',label='Mínimo')
        plt.legend(loc='best', facecolor='w', fontsize=9)
        fig.set_size_inches(12, 6)
        plt.savefig('infomoneda'+moneda,dpi=150, bbox_inches='tight')
        return plt.show()

    def graficarmonedasvwap(self,datos):
        fig, ax = plt.subplots()
        plt.title('ANÁLISIS DEL ' + moneda,fontname='Times New Roman', fontweight='bold' )
        plt.xlabel("Fecha")
        plt.ylabel('Precio en euros')
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.tick_params(axis='x', rotation=60)
        ax.set_facecolor("ivory")
        plt.plot(datos['close'],'turquoise',label='close')
        plt.plot(datos['vwap'],'teal',label='vwap')
        plt.legend(loc='best', facecolor='w', fontsize=9)
        fig.set_size_inches(12, 6)
        plt.savefig('vwap'+moneda,dpi=150, bbox_inches='tight')
        plt.show()

    def candlestick(self,datos):
    
        fig, ax = plt.subplots()

        plt.title('Oscilaciones del precio del ' + moneda,fontname='Times New Roman', fontweight='bold' )
        ax.grid(linestyle='dotted', linewidth=0.6)
        ax.set_facecolor("ivory")

        width = 1.04
        width2 = 1.05
        #define up and down prices
        up = datos[datos.close>=datos.open]
        down = datos[datos.close<datos.open]

        plt.bar(up.index,up.close-up.open,width,bottom=up.open,color='green')
        plt.bar(up.index,up.high-up.close,width2,bottom=up.close,color='green')
        plt.bar(up.index,up.low-up.open,width2,bottom=up.open,color='green')

        plt.bar(down.index,down.close-down.open,width,bottom=down.open,color='red')
        plt.bar(down.index,down.high-down.open,width2,bottom=down.open,color='red')
        plt.bar(down.index,down.low-down.close,width2,bottom=down.close,color='red')

        plt.xticks(rotation=45, ha='right')
        fig.set_size_inches(12, 6)
        plt.savefig('candle'+moneda,dpi=150, bbox_inches='tight')
        return plt.show()


#Ya que la columna de la fecha se ha definido como el indice, se modifica el dataframe
#de forma que ahora la fecha no se encuentra en nanosegundo sino en un formato mas familiar

#aqui habria que meter un input
nsesiones=20
#Definición de funciones para la obtención de la media movil, media movil exponencial y rsi.
def mediamovilsimple(nsesiones): 
    mediamovil=[]    
    for i in range(0,len(datos['close'])-nsesiones):
       suma=0
       for j in range(i,i+nsesiones):
           suma=datos['close'][j]+suma
       mms=(suma/nsesiones)
       mediamovil.append(mms)
       
    return mediamovil

def mediamovilexponencial(nsesiones): 
    multiplicador=2/(nsesiones+1)
    mediamovilexp=[]    
    longitud=len(mediamovilsimple(nsesiones))
    for j in range(0,longitud):
       suma=0
       suma=multiplicador*(mediamovilsimple(nsesiones)[j-1])+(mediamovilsimple(nsesiones)[j-1])+suma
       mme=(suma)
       mediamovilexp.append(mme)
    return mediamovilexp

def rsi(datos, periods = nsesiones, ema = True):
    """
    Returns a pd.Series with the relative strength index.
    """
    close_diff= datos['close'].diff()

    #Es necesario crear dos series: una con periodos alcistas y otros con periodos bajistas
    up = close_diff.clip(lower=0)
    down = -1 * close_diff.clip(upper=0)
    
    if ema == True:
	    # Use exponential moving average
        ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
    else:
        # Use simple moving average
        ma_up = up.rolling(window = periods, adjust=False).mean()
        ma_down = down.rolling(window = periods, adjust=False).mean()
        
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi


#Programa principal

moneda=input("Escibir la moneda:")
fecha=input("Escribir desde que dia se quieren los datos poniendo primero el año, luego el mes y luego el dia, separado con guiones ")
nombre=input("Nombre del csv en el que se guarda la información ")

obtencion_de_datos=obtencion_de_datos()

pairs=obtencion_de_datos.getpairs()
if moneda in list(pairs['altname']):
    moneda=moneda
else:
    print("La moneda introducida no existe")
    moneda= input("Introduzca otra moneda:")
        
datos=obtencion_de_datos.sacardatos(moneda, fecha, nombre)

#Se modifican las fechas para las graficas
fechadata=(datos).index
fechadata=list(fechadata)
datos['new_date'] = [d.date() for d in fechadata]
datos['new_time'] = [d.time() for d in fechadata]

datos['time']=datos['new_date']
datos=datos.drop(['new_time'], axis=1)
datos=datos.drop(['new_date'], axis=1)

#Se definen el numero de periodos que se van a utilizar para calcular la media movil.
nsesiones=20
#Debido a que el calculo de la media movil se ha realizado en orden inverso, se vuelve a voltear
mediamovil=mediamovilsimple(nsesiones)
mediamovil=mediamovil[::-1]

fecha1=datos['time'][nsesiones: ]
graficamms=pd.DataFrame(mediamovil,fecha1)

rsi=rsi(datos, periods = nsesiones, ema = True)
rsi=rsi[::-1]

graficarsi=pd.DataFrame(rsi,fecha1)

#Graficas:
fig, ax = plt.subplots()
plt.title('MEDIA MÓVIL SIMPLE PARA EL ' + moneda ,fontname='Times New Roman', fontweight='bold')
ax.grid(linestyle='dotted', linewidth=0.6)
ax.tick_params(axis='x', rotation=60)
ax.set_facecolor("ivory")
plt.ylabel('Media móvil simple',fontname='Times New Roman', fontweight='bold')
plt.plot(graficamms,'teal',label='mms')
#plt.plot(datos['close'],'SteelBlue',label='close')
plt.legend(loc='best', facecolor='w', fontsize=9)
fig.set_size_inches(12, 6)
plt.savefig('mediamovilsol'+moneda,dpi=150, bbox_inches='tight')

fig, ax = plt.subplots()
plt.title('RSI PARA EL ' + moneda ,fontname='Times New Roman', fontweight='bold')
ax.grid(linestyle='dotted', linewidth=0.6)
ax.tick_params(axis='x', rotation=60)
ax.set_facecolor("ivory")
plt.ylabel('Valor del RSI',fontname='Times New Roman', fontweight='bold')
plt.plot(graficarsi,'SteelBlue',label='RSI')
plt.legend(loc='best', facecolor='w', fontsize=9)
fig.set_size_inches(12, 6)
plt.savefig('rsi'+moneda,dpi=150, bbox_inches='tight')

#Otras graficas
pintar_graficas.graficarmonedas(datos)
pintar_graficas.graficarmonedasvwap(datos)
pintar_graficas.candlestick(datos)