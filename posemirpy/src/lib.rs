use numpy::{PyArray2, PyReadonlyArrayDyn};
use posemir::discovery::algorithm::TecAlgorithm;
use posemir::discovery::siatec_c::SiatecC;
use posemir::point_set::pattern::Pattern;
use posemir::point_set::point::{Point, Point2DRf64};
use posemir::point_set::set::PointSet;
use posemir::point_set::tec::Tec;
use posemir::search::pattern_matcher::{ExactMatcher, PatternMatcher};
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

    fn numpy_array_to_points(np_array: &PyReadonlyArrayDyn<f64>) -> Vec<Point2DRf64> {
        let mut points : Vec<Point2DRf64> = Vec::new();

        for row in np_array.as_array().rows() {
            // Use the raw point from the third column as x
            points.push(Point2DRf64::new(row[2], row[1]));
        }

        points
    }

    #[pyfn(m)]
    #[pyo3(name = "run_siatec_c")]
    fn run_siatec_c<'py>(
        py: Python<'py>,
        np_points_array: PyReadonlyArrayDyn<f64>,
        max_ioi: f64
    ) -> Vec<(&'py PyArray2<f64>, Vec<&'py PyArray2<f64>>)> {

        let point_set = PointSet::new(numpy_array_to_points(&np_points_array));

        let mut patterns: Vec<(&PyArray2<f64>, Vec<&PyArray2<f64>>)> = Vec::new();

        let on_output = |tec: Tec<Point2DRf64>| {
            let pat_array = pattern_to_array(py, &tec.pattern);
            let mut translations = Vec::with_capacity(tec.translators.len());
            for t in &tec.translators {
                translations.push(pattern_to_array(py, &tec.pattern.translate(t)));
            }

            patterns.push((pat_array, translations));
        };

        SiatecC{ max_ioi }.compute_tecs_to_output(&point_set, on_output);

        patterns
    }

    #[pyfn(m)]
    #[pyo3(name = "find_occurrences")]
    fn find_occurrences<'py>(
        py: Python<'py>,
        query_points_array: PyReadonlyArrayDyn<f64>,
        np_points_array: PyReadonlyArrayDyn<f64>,
    ) -> Vec<&'py PyArray2<f64>> {
        let point_set = PointSet::new(numpy_array_to_points(&np_points_array));
        let query_points = numpy_array_to_points(&query_points_array);
        let query_point_refs: Vec<&Point2DRf64> = query_points.iter().map(|p| p).collect();
        let query = Pattern::new(&query_point_refs);

        let mut occurrences = Vec::new();

        let on_output = |pat: Pattern<Point2DRf64>| occurrences.push(pattern_to_array(py, &pat));
        let pattern_matcher = ExactMatcher {};
        pattern_matcher.find_occurrences_with_callback(&query, &point_set, on_output);

        occurrences
    }


    Ok(())
}