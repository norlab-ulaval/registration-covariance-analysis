
#include <iostream>
#include <string>

#include <gflags/gflags.h>
#include "json.hpp"

#include "centered_clustering.h"
#include "nabo_adapter.h"


using namespace recova;
using json = nlohmann::json;

template <class OutIt> void explode(std::string &input, char sep, OutIt out) {
  std::istringstream buffer(input);
  std::string temp;

  while (std::getline(buffer, temp, sep))
    *(out++) = temp;
}


Eigen::MatrixXd json_array_to_matrix(const json& array) {
  int rows = array[0].size();
  int columns = array.size();
  Eigen::MatrixXd eigen_matrix(rows, columns);

  // We transpose the matrix during the copy because libnabo has the points on columns.
  for(int i = 0; i < rows; i++) {
    for(int j = 0; j < columns; j++) {
      eigen_matrix(i,j) = array[j][i];
    }
  }

  return eigen_matrix;
}

DEFINE_int32(n, 12, "Number of elements within radius a point needs to have to be a core point.");
DEFINE_double(radius, 1.0, "Radius within which a point need to have n points to be a core point.");
DEFINE_string(seed, "", "The initial location where to start the cluster. Comma separated list of values representing the vector.");

int main(int argc, char** argv) {
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  json json_dataset;
  std::cin >> json_dataset;

  std::unique_ptr<Eigen::MatrixXd> eigen_dataset(new Eigen::MatrixXd);
  *eigen_dataset = json_array_to_matrix(json_dataset);

  NaboAdapter knn_algorithm;
  knn_algorithm.set_dataset(std::move(eigen_dataset));

  Eigen::VectorXd center = Eigen::VectorXd::Zero(6);
  if(!FLAGS_seed.empty()) {
    std::vector<std::string> elements(6);
    explode(FLAGS_seed, ',', elements.begin());

    for(auto i = 0; i < 6; ++i) {
      center(i) = stof(elements[i]);
    }
  }

  auto cluster = cluster_with_seed(knn_algorithm, center, FLAGS_n, FLAGS_radius);

  json output_document;
  for(auto elt : cluster) {
    output_document.push_back(elt);
  }

  std::cout << output_document << std::endl;

  return 0;
}
