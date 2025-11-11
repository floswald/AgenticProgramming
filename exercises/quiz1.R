library(exams)

exams2html(list.files(pattern = ".Rmd"))

exams2moodle(list.files(pattern = ".Rmd"),edir = "moodles")
