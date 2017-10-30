.PHONY: docs release clean build

clean:
  rm -rf env

build:
  virtualenv env && source env/bin/activate && \
  pip install -r requirements.txt

test: clean build
  source env/bin/activate && \
  python app.py
