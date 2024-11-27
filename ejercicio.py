import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def mostrar_informacion_alumno():
    with st.container(border=True):
        st.markdown('**Legajo:** 59073')
        st.markdown('**Nombre:** Ruiz Tomas Federico')
        st.markdown('**Comisión:** C9')

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

def graficar_ventas(data, producto):
    product_data = data[data['Producto'] == producto].copy()
    product_data['Fecha'] = pd.to_datetime({'year': product_data['Año'], 'month': product_data['Mes'], 'day': 1})
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

def calcular_metricas_producto(datos_producto):

    datos_producto['Precio_promedio'] = datos_producto['Ingreso_total'] / datos_producto['Unidades_vendidas']
    precio_promedio = datos_producto['Precio_promedio'].mean()
    precio_promedio_anual = datos_producto.groupby('Año')['Precio_promedio'].mean()
    variacion_precio_promedio_anual = precio_promedio_anual.pct_change().mean() * 100

    datos_producto['Ganancia'] = datos_producto['Ingreso_total'] - datos_producto['Costo_total']
    datos_producto['Margen'] = (datos_producto['Ganancia'] / datos_producto['Ingreso_total']) * 100
    margen_promedio = datos_producto['Margen'].mean()
    margen_promedio_anual = datos_producto.groupby('Año')['Margen'].mean()
    variacion_margen_promedio_anual = margen_promedio_anual.pct_change().mean() * 100

    unidades_vendidas = datos_producto['Unidades_vendidas'].sum()
    unidades_por_año = datos_producto.groupby('Año')['Unidades_vendidas'].sum()
    variacion_anual_unidades = unidades_por_año.pct_change().mean() * 100

    return {
        'precio_promedio': precio_promedio,
        'variacion_precio': variacion_precio_promedio_anual,
        'margen_promedio': margen_promedio,
        'variacion_margen': variacion_margen_promedio_anual,
        'unidades_vendidas': unidades_vendidas,
        'variacion_unidades': variacion_anual_unidades
    }

def main():
    st.sidebar.header("Cargar archivo de datos")
    uploaded_file = st.sidebar.file_uploader("Subir archivo CSV", type=["csv"])
    
    if uploaded_file is None:
        st.title("Por favor, sube un archivo CSV desde la barra lateral.")
        mostrar_informacion_alumno()
    data = cargar_datos(uploaded_file)

    if data is not None:
        sucursales = ['Todas'] + data['Sucursal'].unique().tolist()
        selected_sucursal = st.sidebar.selectbox("Seleccionar sucursal", sucursales)

        if selected_sucursal != "Todas":
            data = data[data['Sucursal'] == selected_sucursal]

        st.markdown(f"## Datos de {selected_sucursal if selected_sucursal != 'Todas' else 'Todas las Sucursales'}")
        
        for producto in data['Producto'].unique():
            datos_producto = data[data['Producto'] == producto]
            metricas = calcular_metricas_producto(datos_producto)

            with st.container(border=True):
                st.subheader(producto)
                col1, col2 = st.columns([2, 5])
                with col1:
                    st.metric("Precio Promedio", f"${metricas['precio_promedio']:,.0f}", f"{metricas['variacion_precio']:.2f}%")
                    st.metric("Margen Promedio", f"{metricas['margen_promedio']:.0f}%", f"{metricas['variacion_margen']:.2f}%")
                    st.metric("Unidades Vendidas", f"{int(metricas['unidades_vendidas']):,}", f"{metricas['variacion_unidades']:.2f}%")
                with col2:
                    graficar_ventas(data, producto)

if __name__ == "__main__":
    main()