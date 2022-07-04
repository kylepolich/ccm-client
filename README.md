# CCM Client Documentation

## To Build

```
aws s3 sync s3://feaas-prod/user/kyle@dataskeptic.com/ccm/docs/imgs/ docs/imgs/
sphinx-apidoc -f -o docs/source/ src/
cd docs
make latexpdf
```
