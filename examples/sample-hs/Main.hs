import Control.Monad
import Data.Char
import System.IO
import System.IO.Error
import Network
import Network.BSD
import Network.Socket
import System.Environment
import System.Process

main = do [port] <- getArgs
          sock <- socket AF_INET Stream defaultProtocol
          setSocketOption sock ReuseAddr 1
          bind sock $ SockAddrInet (fromInteger $ read port) iNADDR_ANY
          listen sock maxListenQueue
          packages <- readProcess "ghc-pkg" ["list", "--simple-output"] []
          env <- getEnvironment
          let vars = map (\kv -> concat [fst kv, "=", snd kv]) env
          let response = ("HTTP/1.1 200 OK\r\n\r\nWelcome to Haskell Cloud! Chris was here. The following packages are pre-installed:\n\n" ++ unlines (words packages) ++
                          "\n\nAnd here is your environment:\n\n" ++ unlines vars ++ "\n\nTHE END.")
          forever $ do (handle,_,_) <- Network.accept sock
                       request <- hGetContents handle
                       when (any (null . dropWhile isSpace) (lines request)) $ void $ tryIOError $ hPutStr handle response
                       hClose handle
