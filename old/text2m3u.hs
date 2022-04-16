#! /usr/bin/env runhaskell

import HsShellScript (runprog, temp_file, mainwrapper)
import System.Directory (getHomeDirectory)
import System.Environment (getArgs)
import Data.List (intersperse)

main = mainwrapper $ do
    contents <- getContents
    sequence_ $ intersperse (translate "") $ map translate $ lines contents


translate :: String -> IO ()
translate "---" =
    putStrLn "resources/chime.wav"
translate "" =
    putStrLn "resources/pause.wav"
translate line = do
    wav <- temp_file 100 "/tmp/" ".wav"
    txt <- temp_file 100 "/tmp/" ".txt"
    writeFile txt line
    runprog "./read.sh" [txt, wav]
    putStrLn wav
