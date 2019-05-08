#!/usr/bin/env bash
tar -cvf secret.tar secret
gem install travis
travis login
travis encrypt-file secret.tar --add
