FROM ruby:3.4

# Install required packages
RUN apt-get update -qq && apt-get install -y build-essential libpq-dev nodejs

# Create app directory
WORKDIR /app

# Copy and install dependencies
COPY . /app
RUN gem install bundler:2.7.1 && bundle install

# Serve site
CMD ["bundle", "exec", "jekyll", "serve", "--host=0.0.0.0"]