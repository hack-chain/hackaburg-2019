FROM ubuntu

WORKDIR /hack

RUN apt update && apt install -y python3-pip git

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN git clone "https://github.com/m-malikov/privacyscanner" && pip3 install --editable ./privacyscanner 

COPY . .

ENV FLASK_APP="app.py"
ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"

CMD flask run

