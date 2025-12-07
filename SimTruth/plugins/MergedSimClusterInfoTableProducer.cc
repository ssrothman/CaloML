#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "CaloML/DataFormats/interface/MergedSimClusterInfo.h"

#include <vector>
#include <numeric>
#include <string>
#include <array>

class MergedSimClusterInfoTableProducer : public edm::stream::EDProducer<> {
public:
  explicit MergedSimClusterInfoTableProducer(edm::ParameterSet const& params)
      : name_(params.getParameter<std::string>("name")),
        doc_(params.getParameter<std::string>("doc")),
        extension_(params.getParameter<bool>("extension")),
        src_(params.getParameter<edm::InputTag>("src")),
        token_(consumes<std::vector<CaloML::MergedSimClusterInfo>>(src_)) {
    produces<nanoaod::FlatTable>();
  }

  ~MergedSimClusterInfoTableProducer() override {}

  void produce(edm::Event& iEvent, const edm::EventSetup& iSetup) override {
    edm::Handle<std::vector<CaloML::MergedSimClusterInfo>> clusters;
    iEvent.getByToken(token_, clusters);

    std::vector<int> nParticles;

    // invert: array of vectors rather than vector of arrays
    std::array<std::vector<int>, NLEADERS> pdgids;
    std::array<std::vector<float>, NLEADERS> energies;
    std::array<std::vector<float>, NLEADERS> vtx_x, vtx_y, vtx_z, vtx_t;
    std::array<std::vector<float>, NLEADERS> calo_x, calo_y, calo_z, calo_t;
    std::array<std::vector<int>, NLEADERS> reasons;

    std::vector<float> impact_energies;
    std::vector<float> impact_pts;
    std::vector<float> impact_etas;
    std::vector<float> impact_phis;

    size_t nrows = clusters.isValid() ? clusters->size() : 0;

    for (int i = 0; i < NLEADERS; ++i) {
      pdgids[i].reserve(nrows);
      energies[i].reserve(nrows);
      vtx_x[i].reserve(nrows);
      vtx_y[i].reserve(nrows);
      vtx_z[i].reserve(nrows);
      vtx_t[i].reserve(nrows);
      calo_x[i].reserve(nrows);
      calo_y[i].reserve(nrows);
      calo_z[i].reserve(nrows);
      calo_t[i].reserve(nrows);
      reasons[i].reserve(nrows);
    }
    impact_energies.reserve(nrows);
    impact_pts.reserve(nrows);
    impact_etas.reserve(nrows);
    impact_phis.reserve(nrows);

    for (const auto& cl : *clusters) {
      nParticles.push_back(static_cast<int>(cl.pdgids.size()));

      for (unsigned i = 0; i < NLEADERS; ++i) {
        if (i < cl.pdgids.size()) {
          pdgids[i].push_back(cl.pdgids[i]);
          reasons[i].push_back(cl.reasons[i]);
          energies[i].push_back(cl.simTrackInfos[i].momentumAtCalo.E());
          vtx_x[i].push_back(cl.simTrackInfos[i].vtx.x());
          vtx_y[i].push_back(cl.simTrackInfos[i].vtx.y());
          vtx_z[i].push_back(cl.simTrackInfos[i].vtx.z());
          vtx_t[i].push_back(cl.simTrackInfos[i].vtx.t());
          calo_x[i].push_back(cl.simTrackInfos[i].caloImpact.x());
          calo_y[i].push_back(cl.simTrackInfos[i].caloImpact.y());
          calo_z[i].push_back(cl.simTrackInfos[i].caloImpact.z());
          calo_t[i].push_back(cl.simTrackInfos[i].caloImpact.t());
        } else {
          reasons[i].push_back(-1);
          pdgids[i].push_back(0);
          energies[i].push_back(0.f);
          vtx_x[i].push_back(0.f);
          vtx_y[i].push_back(0.f);
          vtx_z[i].push_back(0.f);
          vtx_t[i].push_back(0.f);
          calo_x[i].push_back(0.f);
          calo_y[i].push_back(0.f);
          calo_z[i].push_back(0.f);
          calo_t[i].push_back(0.f);
        }
      }

      math::XYZTLorentzVector impactMomentum;
      for (const auto& info : cl.simTrackInfos) {
        impactMomentum += info.momentumAtCalo;
      }
      impact_energies.push_back(impactMomentum.E());
      impact_pts.push_back(impactMomentum.Pt());
      impact_etas.push_back(impactMomentum.Eta());
      impact_phis.push_back(impactMomentum.Phi());
    }

    auto tab = std::make_unique<nanoaod::FlatTable>(nrows, name_, false, extension_);
    tab->addColumn<int>("nParticles", nParticles, "Number of contributing sim particles");

    // add per-leader columns
    for (int i = 0; i < NLEADERS; ++i) {
      std::string pdgName = "pdg" + std::to_string(i);
      std::string enName = "energy" + std::to_string(i);

      tab->addColumn<int>(pdgName, pdgids[i], "Leading PDG id (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(enName, energies[i], "Energy contribution of leading particle (rank " + std::to_string(i) + ")");

      std::string vtx_x_name = "vtx_x" + std::to_string(i);
      std::string vtx_y_name = "vtx_y" + std::to_string(i);
      std::string vtx_z_name = "vtx_z" + std::to_string(i);
      std::string vtx_t_name = "vtx_t" + std::to_string(i);

      tab->addColumn<float>(vtx_x_name, vtx_x[i], "x coordinate of vertex of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(vtx_y_name, vtx_y[i], "y coordinate of vertex of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(vtx_z_name, vtx_z[i], "z coordinate of vertex of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(vtx_t_name, vtx_t[i], "t coordinate of vertex of leading particle (rank " + std::to_string(i) + ")");

      std::string calo_x_name = "calo_x" + std::to_string(i);
      std::string calo_y_name = "calo_y" + std::to_string(i);
      std::string calo_z_name = "calo_z" + std::to_string(i);
      std::string calo_t_name = "calo_t" + std::to_string(i);

      tab->addColumn<float>(calo_x_name, calo_x[i], "x coordinate of calo impact of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(calo_y_name, calo_y[i], "y coordinate of calo impact of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(calo_z_name, calo_z[i], "z coordinate of calo impact of leading particle (rank " + std::to_string(i) + ")");
      tab->addColumn<float>(calo_t_name, calo_t[i], "t coordinate of calo impact of leading particle (rank " + std::to_string(i) + ")");
    
      std::string reason_name = "reason" + std::to_string(i);
      tab->addColumn<int>(reason_name, reasons[i], "Merge reason for leading particle (rank " + std::to_string(i) + ")"); 
    }

    tab->addColumn<float>("impact_energy", impact_energies, "Total energy at calo impact summed over all contributing particles");
    tab->addColumn<float>("impact_pt", impact_pts, "Total pt at calo impact summed over all contributing particles");
    tab->addColumn<float>("impact_eta", impact_etas, "Eta of total momentum at calo impact summed over all contributing particles");
    tab->addColumn<float>("impact_phi", impact_phis, "Phi of total momentum at calo impact summed over all contributing particles");

    iEvent.put(std::move(tab));
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src", edm::InputTag(""));
    desc.add<std::string>("name", "MergedSimCluster");
    desc.add<std::string>("doc", "Merged sim cluster table");
    desc.add<bool>("extension", false);
    descriptions.add("mergedSimClusterInfoTableProducer", desc);
  }

private:
  const std::string name_, doc_;
  const bool extension_;
  const edm::InputTag src_;
  edm::EDGetTokenT<std::vector<CaloML::MergedSimClusterInfo>> token_;

  static constexpr int NLEADERS = 4;
};

DEFINE_FWK_MODULE(MergedSimClusterInfoTableProducer);
