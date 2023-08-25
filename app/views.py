from flask import render_template, request, redirect, url_for, send_from_directory
from . import app, db
from . import level1_plots as level1_plots_module
from . import level2_plots as l2pm
from .create_all import Level1File
from sqlalchemy import func

from astropy.time import Time 

PLOT_PREFIXES = ["vane_fit_", "skydip_","feed"] 

@app.route('/level1_plots/<plot_type>', methods=['GET', 'POST'])
def level1_plots(plot_type='mean_Tvane'):
    # Default values
    min_mjd = db.session.query(func.min(Level1File.mjd)).scalar()
    max_mjd = db.session.query(func.max(Level1File.mjd)).scalar()
    start_date_default = Time(min_mjd, format='mjd').to_value('iso', 'date')
    end_date_default = Time(max_mjd, format='mjd').to_value('iso', 'date')
    
    if request.method == 'POST':
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        start_mjd = Time(start_date, format='iso').mjd
        end_mjd = Time(end_date, format='iso').mjd
        print('HELLO FROM POST')
        level1_plots_module.generate_plots(plot_type=plot_type,start_mjd=start_mjd, end_mjd=end_mjd)
    else:
        print('HELLO FROM GET')
        start_date = start_date_default
        end_date = end_date_default
        level1_plots_module.generate_plots(plot_type=plot_type,start_mjd=min_mjd, end_mjd=max_mjd)  # This will generate the default plots

    return render_template('level1_plots.html', plot_type=plot_type, start_date=start_date, end_date=end_date)


@app.route('/update_plots', methods=['POST'])
def update_plots():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    plot_type = request.form.get("plot_type")  # Capture the plot_type from form
    
    start_mjd = Time(start_date, format='iso').mjd
    end_mjd = Time(end_date, format='iso').mjd
    
    level1_plots_module.generate_plots(plot_type=plot_type, start_mjd=start_mjd, end_mjd=end_mjd)
    
    # Redirect to the specific plot_type
    return redirect(url_for('level1_plots', plot_type=plot_type))

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/level1_index')
def level1_index():
    return render_template('level1_index.html')

@app.route('/monthly_map_index')
def monthly_map_index():
    return render_template('monthly_map_index.html')

@app.route('/level2_index')
def level2_index():
    months = l2pm.get_available_months()
    return render_template('level2_index.html', months=months)

@app.route('/level2_index/<month>')
def level2_sources(month):
    sources = l2pm.get_sources_for_month(month)
    return render_template('level2_sources.html', month=month, sources=sources)

@app.route('/level2_plots/<month>/<source>')
def level2_observations(month, source):
    observations = l2pm.get_observations_for_source(month, source)
    return render_template('level2_observations.html', month=month, source=source, observations=observations)

@app.route('/level2_plots/<month>/<source>/<observation>')
def level2_plot_list(month, source, observation):
    plots = l2pm.get_plots_for_observation(month, source, observation, PLOT_PREFIXES)
    return render_template('level2_plot_list.html', month=month, source=source, observation=observation, plots=plots)

@app.route('/external_image/<month>/<source>/<observation>/<filename>')
def external_image(month, source, observation, filename):
    # Define your external directory
    import os 
    image_path = os.path.join(l2pm.LEVEL2_DIR, month, source, "figures", observation)
    print(image_path)
    return send_from_directory(image_path, filename)
