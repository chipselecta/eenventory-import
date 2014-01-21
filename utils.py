from subprocess import call

cookies = ''

def wget(url, file):
    call(['wget',
          '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0',
          '--no-check-certificate',
          '--load-cookies', cookies,
          url,
          '-O', file])
