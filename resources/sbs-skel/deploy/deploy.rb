# config valid only for Capistrano 3.1
lock '3.1.0'

set :application, '%SRV_USER%'
set :repo_url, '%GIT_REPO%'

# Default branch is :master
# ask :branch, proc { `git rev-parse --abbrev-ref HEAD`.chomp }

# Default deploy_to directory is /var/www/my_app
set :deploy_to, '/home/%SRV_USER%/sbsmgr'

# Default value for :scm is :git
# set :scm, :git

# Default value for :format is :pretty
# set :format, :pretty

# Default value for :log_level is :debug
# set :log_level, :debug

# Default value for :pty is false
# set :pty, true

# Default value for :linked_files is []
#set :linked_files, %w{server.pid}

# Default value for linked_dirs is []
set :linked_dirs, %w{logs tmp attachments namedfiles intrafiles}

# Default value for default_env is {}
# set :default_env, { path: "/opt/ruby/bin:$PATH" }

# Default value for keep_releases is 5
set :keep_releases, 2

# Enable submodules
set :git_strategy, SubmoduleStrategy

namespace :deploy do

  desc 'Starting application'
  task :start do
    on roles(:app), in: :sequence, wait: 5 do
      execute :sudo, 'service %SERVICE_NAME% start'
    end
  end

  desc 'Stopping application'
  task :stop do
    on roles(:app), in: :sequence, wait: 5 do
      execute :sudo, 'service %SERVICE_NAME% stop; true'
    end
  end

  desc 'Restart application'
  task :restart do
    on roles(:app), in: :sequence, wait: 5 do
      execute :sudo, 'service %SERVICE_NAME% stop; true'
      #within release_path do
      #  execute '/opt/sbs-play/play', 'dependencies'
      #end
      execute :sudo, 'service %SERVICE_NAME% start'
    end
  end

  after :publishing, :restart

  after :finishing, "deploy:cleanup"

end
