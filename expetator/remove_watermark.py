import expetator.bundle as bundle
import expetator.monitoring_csv as monitoring_csv
import expetator.monitoring_list as monitoring_list
import expetator.watermark as watermark
import sys

def remove_watermark(target_file, target_dir):

    bundle_data, zip_fid = bundle.init_bundle(target_file)

    try:
        moj = monitoring_csv.read_bundle_csv('mojitos', bundle_data, zip_fid)
        moj_cleaned = watermark.remove_watermark_blocks(moj, frequency=20)
    except:
        moj_cleaned = None

    try:
        power = monitoring_list.read_bundle_list('power', bundle_data, zip_fid)
        power_cleaned = watermark.remove_watermark_blocks(power, frequency=20)
    except:
        power_cleaned = None

    watermark.remove_wt_name(bundle_data)
    if target_file.endswith('.zip'):
        target_file = target_file[:-4]

    bundle.save_bundle(target_file, bundle_data, target_dir)

    if not moj_cleaned is None:
        monitoring_csv.write_bundle_csv('mojitos', bundle_data, moj_cleaned, target_dir)
    if not power_cleaned is None:
        monitoring_list.write_bundle_list('power', bundle_data, power_cleaned, target_dir)

def main():
    if len(sys.argv) != 3:
        print('Usage : %s main_file target_directory')
        sys.exit(0)

    target_file = sys.argv[1]
    target_dir = sys.argv[2]
    remove_watermark(target_file, target_dir)

if __name__ == '__main__':
    main()
