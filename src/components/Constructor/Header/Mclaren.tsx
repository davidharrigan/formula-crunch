import Image from "next/image";

const MclarenHeader = () => {
  return (
    <>
      <div className={`bg-mclaren w-100 h-6`}>
        <div className="flex w-100 place-content-center">
          <Image
            src="/constructors/mclaren.svg"
            width={80}
            height={80}
            alt="Mclaren Logo"
          />
        </div>
      </div>
    </>
  );
};

export default MclarenHeader;
