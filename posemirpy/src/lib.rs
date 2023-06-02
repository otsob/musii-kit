use numpy::{PyArray2, PyReadonlyArrayDyn};
use posemir::discovery::algorithm::TecAlgorithm;
use posemir::discovery::siatec_c::SiatecC;
use posemir::point_set::pattern::Pattern;
use posemir::point_set::point::{Point, Point2DRf64};
use posemir::point_set::set::PointSet;
use pyo3::{pymodule, types::PyModule, PyResult, Python};


/// The Python module definition
#[pymodule]
fn posemirpy(_py: Python<'_>, m: &PyModule) -> PyResult<()> {

    fn pattern_to_array<'py>(py: Python<'py>, pattern: &Pattern<Point2DRf64>) -> &'py PyArray2<f64> {
        let arr = unsafe {
            let rows = pattern.len();
            let cols = 2;
            let arr = PyArray2::<f64>::new(py, [rows, cols], false);

            for i in 0..rows {
                let p = pattern[i];
                arr.uget_raw([i, 0]).write(p.get_raw_x());
                arr.uget_raw([i, 1]).write(p.component_f64(1).unwrap());
            }

            arr
        };

        arr
    }

    #[pyfn(m)]
    #[pyo3(name = "run_siatec_c")]
    fn run_siatec_c<'py>(
        py: Python<'py>,
        np_points_array: PyReadonlyArrayDyn<f64>,
        max_ioi: f64
    ) -> Vec<(&'py PyArray2<f64>, Vec<&'py PyArray2<f64>>)> {

        let mut points : Vec<Point2DRf64> = Vec::new();

        for row in np_points_array.as_array().rows() {
            // Use the raw point from the third column as x
            points.push(Point2DRf64::new(row[2], row[1]));
        }

        let point_set = PointSet::new(points);
        let tecs = SiatecC{ max_ioi }.compute_tecs(&point_set);

        let mut patterns: Vec<(&PyArray2<f64>, Vec<&PyArray2<f64>>)> = Vec::with_capacity(tecs.len());

        for tec in &tecs {
            let pat_array = pattern_to_array(py, &tec.pattern);
            let mut translations = Vec::with_capacity(tec.translators.len());
            for t in &tec.translators {
                translations.push(pattern_to_array(py, &tec.pattern.translate(t)));
            }

            patterns.push((pat_array, translations));
        }

        patterns
    }

    Ok(())
}