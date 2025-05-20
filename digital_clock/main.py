import streamlit as st
import datetime
import time

class DigitalClock:
    """A digital clock that provides time functionality"""

    def __init__(self,use_24_hr_format=False):
        self.use_24_hr_format=use_24_hr_format

    def get_current_time(self):
         """Get the current time
            Returns:
            str: Formatted current time string"""
         now=datetime.datetime.now()
         if self.use_24_hr_format:
             return now.strftime("%H:%M:%S")
         else:
             return now.strftime("%I:%M:%S:%p")
         
    def get_current_date(self):
        """Get the current date
            Returns:
            str: Formatted current date string"""
        now=datetime.datetime.now()
        return now.strftime("%B:%d:%Y")
    
    def toggle_format(self):
        """Toggle between 12 hour and 24-hour formats"""
        self.use_24_hr_format=not self.use_24_hr_format
        return self.use_24_hr_format
    
def main():
    st.set_page_config(
        page_title="Digital Clock",
        page_icon="⏰"
    )

    #check if clock object already exists in session state
    if "clock" not in st.session_state:
        st.session_state.clock=DigitalClock()

    st.title("Digital Clock")

    col1,col2=st.columns([3,1])

    with col2:
        if st.button("Toggle 12/24 Hour"):
            is_24hr=st.session_state.clock.toggle_format()
            format_text="24-Hour" if is_24hr else "12-Hour"
            st.write(f"Using {format_text} format")

    with col1:
        format_text="24-Hour" if st.session_state.clock.use_24_hr_format else "12-Hour"
        st.write(f"Currently using {format_text} format")

    time_placeholder=st.empty()
    date_placeholder=st.empty()

    while True:
        current_time=st.session_state.clock.get_current_time()
        current_date=st.session_state.clock.get_current_date()

        time_placeholder.markdown(f"<h1 style='text-align: center; font-size: 72px;'>{current_time}</h1>",unsafe_allow_html=True)
        date_placeholder.markdown(f"<h3 style='text-align: center;'>{current_date}</h3>", unsafe_allow_html=True)

        time.sleep(1)

if __name__=="__main__":
    main()