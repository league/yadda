FROM zsol/haskell-platform-2013.2.0.0
MAINTAINER Christopher League <league@contrapunctus.net>
ADD . /app
RUN cd /app && cabal build
EXPOSE 5000
CMD cd /app && cabal run server -- 5000 +RTS -N
