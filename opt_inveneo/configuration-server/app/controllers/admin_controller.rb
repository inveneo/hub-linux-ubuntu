class AdminController < ApplicationController
  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    @initial_config_pages, @initial_configs = paginate :initial_configs, :per_page => 10
  end

  def show
    @initial_config = InitialConfig.find(params[:id])
  end

  def new
    @initial_config = InitialConfig.new
  end

  def create
    @initial_config = InitialConfig.new(params[:initial_config])
    if @initial_config.save
      flash[:notice] = 'InitialConfig was successfully created.'
      redirect_to :action => 'list'
    else
      render :action => 'new'
    end
  end

  def edit
    @initial_config = InitialConfig.find(params[:id])
  end

  def update
    @initial_config = InitialConfig.find(params[:id])
    if @initial_config.update_attributes(params[:initial_config])
      flash[:notice] = 'InitialConfig was successfully updated.'
      redirect_to :action => 'show', :id => @initial_config
    else
      render :action => 'edit'
    end
  end

  def destroy
    InitialConfig.find(params[:id]).destroy
    redirect_to :action => 'list'
  end
end
