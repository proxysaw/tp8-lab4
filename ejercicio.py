import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## ATENCION: Debe colocar la direccion en la que ha sido publicada la aplicacion en la siguiente linea\
# url = 'https://tp8-555555.streamlit.app/'

def mostrar_informacion_alumno():
    with st.container(border=True):
        st.markdown('**Legajo:** 59073')
        st.markdown('**Nombre:** Ruiz Tomas Federico')
        st.markdown('**Comisión:** C9')

mostrar_informacion_alumno()

st.markdown(
    """
    <style>
    .metric-container {
        display: flex;
        flex-direction: column;
        justify-content: center; 
        height: 50px; 
    }
    .stMetric {
        font-size: 1.5rem; 
        margin: 0; 
    }
    .product-header {
        font-size: 2.5rem; 
        font-weight: bold; 
        margin-bottom: 10px;
        color: #FFFFFF; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def cargar_datos(uploaded_file):
    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            required_columns = ['Sucursal', 'Producto', 'Año', 'Mes', 'Unidades_vendidas', 'Ingreso_total', 'Costo_total']
            if all(col in data.columns for col in required_columns):
                data['Producto'] = pd.Categorical(data['Producto'], categories=data['Producto'].unique(), ordered=True)
                return data
            else:
                st.error("El archivo no contiene las columnas requeridas.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
    return None

def calcular_precio_promedio(data):
    return data['Ingreso_total'] / data['Unidades_vendidas']

def calcular_margen_promedio(data):
    return ((data['Ingreso_total'] - data['Costo_total']) / data['Ingreso_total']) * 100

def calcular_unidades_totales(data):
    return data['Unidades_vendidas'].sum()

def calcular(data):
    grouped = data.groupby('Producto').agg({  
        'Unidades_vendidas': 'sum',
        'Ingreso_total': 'sum',
        'Costo_total': 'sum'
    }).reset_index()
    
    grouped['Precio Promedio'] = calcular_precio_promedio(grouped)
    grouped['Margen Promedio'] = calcular_margen_promedio(grouped)
    
    if 'variaciones' not in st.session_state:
        st.session_state['variaciones'] = {
            'Var. Precio': np.random.uniform(-5, 5, len(grouped)),
            'Var. Margen': np.random.uniform(-5, 5, len(grouped)),
            'Var. Ventas': np.random.uniform(-10, 10, len(grouped))
        }

    for var in ['Var. Precio', 'Var. Margen', 'Var. Ventas']:
        grouped[var] = st.session_state['variaciones'][var]
        
    return grouped


def graficar_ventas(data, producto):
    product_data = data[data['Producto'] == producto].copy()
    product_data['Fecha'] = pd.to_datetime({
        'year': product_data['Año'], 
        'month': product_data['Mes'], 
        'day': 1
    })
    product_data = product_data.groupby('Fecha', as_index=False)['Unidades_vendidas'].sum()
    x = np.arange(len(product_data))
    z = np.polyfit(x, product_data['Unidades_vendidas'], 1)
    p = np.poly1d(z)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(product_data['Fecha'], product_data['Unidades_vendidas'], label=producto, color='blue', linewidth=1.5)
    ax.plot(product_data['Fecha'], p(x), "r--", label='Tendencia', linewidth=2)
    ax.set_title(f"Evolución de Ventas Mensual - {producto}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Fecha", fontsize=10)
    ax.set_ylabel("Unidades Vendidas", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', fontsize=9)
    ax.tick_params(axis='x', labelrotation=45, labelsize=8)
    st.pyplot(fig)

def mostrar(data, row):
    st.markdown(
        f"<div class='product-header'>{row['Producto']}</div>",
        unsafe_allow_html=True
    )
    with st.container(border=True):
        col1, col2 = st.columns([2, 5])  
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Precio Promedio", f"${row['Precio Promedio']:.2f}", f"{row['Var. Precio']:.2f}%")
        st.metric("Margen Promedio", f"{row['Margen Promedio']:.2f}%", f"{row['Var. Margen']:.2f}%")
        st.metric("Unidades Vendidas", f"{int(row['Unidades_vendidas']):,}", f"{row['Var. Ventas']:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        graficar_ventas(data, row['Producto'])

def main():
    st.sidebar.header("Cargar archivo de datos")
    uploaded_file = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])
    data = cargar_datos(uploaded_file)
    
    if data is not None:
        sucursales = ['Todas'] + data['Sucursal'].unique().tolist()
        selected_sucursal = st.sidebar.selectbox("Seleccionar sucursal", sucursales)
        
        if selected_sucursal != "Todas":
            data = data[data['Sucursal'] == selected_sucursal]

        grouped = calcular(data)
        st.markdown(f"## Datos de {selected_sucursal if selected_sucursal != 'Todas' else 'Todas las Sucursales'}")
        for _, row in grouped.iterrows():
            mostrar(data, row)
    else:
        st.info("Por favor, sube un archivo CSV desde la barra lateral.")

if __name__ == "__main__":
    main()
