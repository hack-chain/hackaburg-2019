FROM ubuntu

WORKDIR /hack

RUN apt update && apt install -y python3 python3-pip python3-dev git wget

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
RUN apt update && apt install -y google-chrome-stable chromium-browser

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN git clone "https://github.com/m-malikov/privacyscanner" && pip3 install --editable ./privacyscanner 
RUN privacyscanner update_dependencies

COPY . .

ENV FLASK_APP="app.py"
ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"

CMD flask run

