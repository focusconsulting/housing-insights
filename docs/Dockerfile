FROM ruby

COPY Gemfile* /srv/jekyll/
WORKDIR /srv/jekyll

RUN bundle install

ENTRYPOINT ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--watch", "--incremental", "--force_polling"]

EXPOSE 4000

