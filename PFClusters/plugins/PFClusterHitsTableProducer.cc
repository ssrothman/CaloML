#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/ParticleFlowReco/interface/PFCluster.h"
#include "DataFormats/ParticleFlowReco/interface/PFRecHit.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloCellGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/EcalDetId/interface/EcalSubdetector.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "DataFormats/EcalDetId/interface/ESDetId.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"

#include <vector>

class PFClusterHitsTableProducer : public edm::stream::EDProducer<> {
public:
	explicit PFClusterHitsTableProducer(const edm::ParameterSet& params)
			: src_(consumes<std::vector<reco::PFCluster>>(params.getParameter<edm::InputTag>("src"))),
              name_(params.getParameter<std::string>("name")),
              doc_(params.getParameter<std::string>("doc")),
              cut_(params.getParameter<std::string>("cut"), true),
              caloGeoToken_(edm::stream::EDProducer<>::esConsumes<edm::Transition::BeginRun>()) {
		produces<nanoaod::FlatTable>();
	}

	~PFClusterHitsTableProducer() override = default;

	static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
		edm::ParameterSetDescription desc;
		desc.add<edm::InputTag>("src", edm::InputTag("particleFlowClusterHGCal"));
		desc.add<std::string>("name", "pfClusterRecHit");
		desc.add<std::string>("doc", "Table of PFRecHits associated to reco::PFCluster objects");
		desc.add<std::string>("cut", "");
		descriptions.add("pfClusterHitsTableProducer", desc);
	}

	void beginRun(const edm::Run&, const edm::EventSetup& iSetup) override {
		geometry_ = &iSetup.getData(caloGeoToken_);
	}

	GlobalPoint getPositionFromDetId(DetId id) {
		DetId::Detector det = id.det();
		if (det == DetId::Ecal) {
			EcalSubdetector subdet = static_cast<EcalSubdetector>(id.subdetId());
			if (subdet == EcalBarrel) {
				EBDetId ebId(id);
				const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalBarrel);
				return cellGeometry->getGeometry(ebId)->getPosition();
			} else if (subdet == EcalEndcap) {
				EEDetId eeId(id);
				const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalEndcap);
				return cellGeometry->getGeometry(eeId)->getPosition();
			} else if (subdet == EcalPreshower) {
				ESDetId esId(id);
				const auto& cellGeometry = geometry_->getSubdetectorGeometry(DetId::Ecal, EcalPreshower);
				return cellGeometry->getGeometry(esId)->getPosition();
			}
		} else if (det == DetId::Hcal) {
			HcalDetId hcalId(id);
			const HcalGeometry *cellGeometry = dynamic_cast<const HcalGeometry *>(geometry_->getSubdetectorGeometry(hcalId));
			return cellGeometry->getPosition(hcalId);
		}
		throw cms::Exception("PFClusterHitsTableProducer") << "Unsupported DetId type " << det;
	}

	void produce(edm::Event& event, const edm::EventSetup&) override {
		edm::Handle<std::vector<reco::PFCluster>> clusters;
		event.getByToken(src_, clusters);

		std::vector<int> clusterIdx;

		std::vector<float> clusterEnergy;
		std::vector<float> recHitEnergy;
		std::vector<float> recHitTime;
		std::vector<float> recHitFractionInCluster;
		std::vector<float> recHitEnergyInCluster;
		std::vector<float> eta;
		std::vector<float> phi;
		std::vector<float> x;
		std::vector<float> y;
		std::vector<float> z;
		std::vector<int> det;
		std::vector<int> subdet;
		std::vector<int> depth;
		std::vector<int> flags;
		std::vector<unsigned int> detId;

		for (size_t iCluster = 0; iCluster < clusters->size(); ++iCluster) {
			const auto& cluster = clusters->at(iCluster);
			if (!cut_(cluster)) {
				continue;
			}

			for (const auto& hitRefAndFraction : cluster.recHitFractions()) {
				const auto& hitRef = hitRefAndFraction.recHitRef();
				if (hitRef.isNull() || !hitRef.isAvailable()) {
                    printf("Warning: Invalid PFRecHitRef in PFCluster at index %zu, skipping this hit.\n", iCluster);
					continue;
				}

				const reco::PFRecHit& recHit = *hitRef;
				const float frac = hitRefAndFraction.fraction();
				const DetId recHitDetId(recHit.detId());
				const int recHitDepth = recHit.depth();
				const int recHitFlags = static_cast<int>(recHit.flags());

				const GlobalPoint pos = getPositionFromDetId(recHitDetId);

				clusterIdx.push_back(static_cast<int>(iCluster));
				clusterEnergy.push_back(cluster.energy());
				recHitEnergy.push_back(recHit.energy());
				recHitTime.push_back(recHit.time());
				recHitFractionInCluster.push_back(frac);
				recHitEnergyInCluster.push_back(frac * recHit.energy());
				eta.push_back(pos.eta());
				phi.push_back(pos.phi());
				x.push_back(pos.x());
				y.push_back(pos.y());
				z.push_back(pos.z());
				det.push_back(recHitDetId.det());
				subdet.push_back(recHitDetId.subdetId());
				depth.push_back(recHitDepth);
				flags.push_back(recHitFlags);
				detId.push_back(recHitDetId.rawId());
			} // end for RecHits in cluster
		} // end for clusters

		auto table = std::make_unique<nanoaod::FlatTable>(recHitEnergy.size(), name_, false, false);
		table->addColumn<int>("clusterIdx", clusterIdx, "Index of parent PFCluster in input collection");
		table->addColumn<float>("clusterEnergy", clusterEnergy, "Parent PFCluster energy [GeV]");
		table->addColumn<float>("energy", recHitEnergy, "PFRecHit energy [GeV]");
		table->addColumn<float>("time", recHitTime, "PFRecHit time");
		table->addColumn<float>("fractionInCluster", recHitFractionInCluster, "PFRecHit fraction in parent PFCluster");
		table->addColumn<float>("energyInCluster", recHitEnergyInCluster, "PFRecHit energy contribution in parent PFCluster [GeV]");
		table->addColumn<float>("eta", eta, "PFRecHit pseudorapidity");
		table->addColumn<float>("phi", phi, "PFRecHit azimuthal angle");
		table->addColumn<float>("x", x, "PFRecHit x position [cm]");
		table->addColumn<float>("y", y, "PFRecHit y position [cm]");
		table->addColumn<float>("z", z, "PFRecHit z position [cm]");
		table->addColumn<int>("det", det, "Detector enum from DetId::det()");
		table->addColumn<int>("subdet", subdet, "Subdetector enum from DetId::subdetId()");
		table->addColumn<int>("depth", depth, "PFRecHit depth index");
		table->addColumn<int>("flags", flags, "PFRecHit flags bitfield");
		table->addColumn<unsigned int>("detId", detId, "Raw detector ID");

		event.put(std::move(table));
	}

private:
	edm::EDGetTokenT<std::vector<reco::PFCluster>> src_;
	const std::string name_;
	const std::string doc_;
	const StringCutObjectSelector<reco::PFCluster> cut_;
	edm::ESGetToken<CaloGeometry, CaloGeometryRecord> caloGeoToken_;
	const CaloGeometry* geometry_;
};

DEFINE_FWK_MODULE(PFClusterHitsTableProducer);
