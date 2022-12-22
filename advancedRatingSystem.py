import streamlit as st
from crawlers import Amazon, HepsiBurada, N11, Trendyol
from time  import sleep

if __name__ == "__main__":  

    if 'scraperDisabled' not in st.session_state:
        st.session_state.scraperDisabled = False
    if 'crawlDataDisabled' not in st.session_state:
        st.session_state.crawlDataDisabled = False
    if 'trainingDisabled' not in st.session_state:
        st.session_state.trainingDisabled = False
    if 'downloadFileDisabled' not in st.session_state:
        st.session_state.downloadFileDisabled = False

    def disableAll():
        st.session_state["scraperDisabled"] = True 
        st.session_state["crawlDataDisabled"] = True
        st.session_state["trainingDisabled"] = True
        st.session_state["downloadFileDisabled"] = True

    def enableAll():
        st.session_state["scraperDisabled"] = False 
        st.session_state["crawlDataDisabled"] = False
        st.session_state["trainingDisabled"] = False
        st.session_state["trainingDisadownloadFileDisabledled"] = False

    dataScraper = st.sidebar.selectbox(
        'Choose a data scraper',
        ("HepsiBurada", "Amazon", "Trendyol", "N11"), disabled = st.session_state.get("scraperDisabled", True)
    )

    st.sidebar.text("\n\n\n")

    try:
        with open(f"commentData{dataScraper}.xlsx", "rb") as file:
            btn = st.sidebar.download_button(
                    label=f"Download the comments file {dataScraper}.xlsx",
                    data=file,
                    file_name=f"commentData{dataScraper}.xlsx",
                    disabled = st.session_state.get("scraperDisabled", True),
                )
    except:
        pass

    st.title('ADVANCED RATING SYSTEM')
    
    col_1, col_2 = st.columns(2)  
    crawlDataButton = col_1.button(f'Get comments from {dataScraper}', on_click=disableAll, disabled=st.session_state.get("crawlDataDisabled", True))
    trainDataButton = col_2.button(f'Get rating for {dataScraper}', on_click=disableAll, disabled=st.session_state.get("crawlDataDisabled", True))

    if crawlDataButton:
        with st.spinner(f'Wait for getting the comments of {dataScraper}'):
            match dataScraper:
                case "HepsiBurada": 
                    hepsiBurada = HepsiBurada()
                    hepsiBurada.crawlData()                     
                case "Amazon":
                    amazon = Amazon()
                    amazon.crawlData()
                case "Trendyol":
                    trendyol = Trendyol()
                    trendyol.crawlData() 
                case "N11":
                    n11 = N11()
                    n11.crawlData() 
                    
        col_1.success(f"{dataScraper} Done!")    
        sleep(10)    
        enableAll()
        st.experimental_rerun()
       
    if trainDataButton:
        col_2.write(f"rating")
        sleep(5)
        enableAll()
        st.experimental_rerun()
